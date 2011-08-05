
import sys
import os
import imp
from traceback import format_exception

class Module:

    def __init__(self, name, module, obj, functions):
        self.name = name
        self.module = module
        self.object = obj
        self.functions = functions
        self.aliases = obj.aliases if hasattr(obj, 'aliases') else None
             

    def __str__(self):
        ' :3 '
        return "{'name': %s, 'module': %s, 'object': %s, 'functions': %s}" % \
                    (self.name, self.module, self.object, self.functions) 

class Dependences(object):
    "If you use modules with same names, you need to use full names through getitem."
    def __setitem__(self, item, value):
        setattr(self, item, value)
        if item.find('.') >= 0:
            setattr(self, item.rsplit('.', 1)[-1], value)
    def __getattr__(self, item):
        try:
            return self.__getitem__(item)
        except KeyError:
            return None

class Manager:

    def __init__(self):
        self.modules = {}
        self.functions = {}
        self.aliases = {}
        self.__loading = []
        self.directory = 'plugins'
        self.load_dir()

    def load_dir(self, directory=None):
        directory = directory or self.directory
        print "Loading dir " + directory
        for fname in os.listdir(directory):
            if fname.endswith('.py'):
                plugin_name = fname.rsplit('.', 1)[0]
                if plugin_name != '__init__':
                    modulename = '.'.join((directory, plugin_name))
                    try:
                        self.load(modulename)
                    except:
                        print "Could not load %s:" % plugin_name
                        print ''.join(format_exception(*sys.exc_info()))
                    finally:
                        self.__loading.remove(modulename)
        self.update_functions()

    def load(self, modulename):
        if modulename in self.__loading:
            return
        print "Loading " + modulename
        module = None
        self.__loading.append(modulename)
        try:
            module = self._reload_hook(self.modules[modulename].module)
        except KeyError:
            module = self._import_hook(modulename, fromlist='*')
        finally:
            if self.modules.has_key(modulename):
                del self.modules[modulename]
        if module:
            obj = self.__get_objects(module)
            if obj:
                obj = obj()
                #FIXME: Dependencies loads after module imported
                #TODO: Dependencies needs full path
                functions = self.__get_functions(obj)
                self.modules[modulename] = Module(modulename, module, obj, functions)
                if hasattr(obj, 'depends'):                    
                    depends = Dependences()
                    for depend in obj.depends:
                        self.load(depend)
                        mdep = self.modules.get(depend)
                        if mdep:
                            mdep = mdep.obj
                        setattr(depends, depend, mdep)
                    setattr(obj, 'depends', depends)
        

    def get(self, name):
        if name in self.modules:
            return self.modules[name]

    def __get_objects(self, module):
        #FIXME: Too lazy
        #TODO: many modules in one file
        objs = None
        for membername in dir(module):
            member = getattr(module, membername)
            if type(member).__name__ == 'classobj' and hasattr(member, '_marvinModule'):
                setattr(member, 'manager', self)
                objs = member
        return objs

    def __get_functions(self, obj):
        ''' Checks for public functions presence
            and returns list of avaliable.
        '''
        real = {}
        public = getattr(obj, 'public')
        for function in public:
            try:
                func = getattr(obj, function)
            except Exception, e:
                print 'Bad function %s: %s' % (function, e)
                continue
            real[function] = func
        return real

    def update_functions(self):
        self.functions = {}
        self.aliases = {}
        for m in self.modules.values():
            for func in m.functions.keys():
                if func in self.functions.keys():
                    print 'Function %s already loaded in module %s. Skipped in %s.' % \
                            (func, self.functions[func], m.name)
                    continue
                if func in m.aliases.keys():
                    for alias in m.aliases[func]:
                        if alias in self.aliases:
                            print 'Alias %s already loaded for function %s in module %s. Skipped for %s.' % \
                            (alias, self.aliases[alias], m.name, func)
                            continue
                        self.aliases[alias] = func
                self.functions[func] = m.name

    def _import_hook(self, name, globals=None, locals=None, fromlist=None):
        parent = self.__determine_parent(globals)
        q, tail = self.__find_head_package(parent, name)
        m = self.__load_tail(q, tail)
        if not fromlist:
            return q
        if hasattr(m, "__path__"):
            self.__ensure_fromlist(m, fromlist)
        return m

    def __determine_parent(self, globals):
        if not globals or not globals.has_key("__name__"):
            return None
        pname = globals['__name__']
        if globals.has_key("__path__"):
            parent = sys.modules[pname]
            assert globals is parent.__dict__
            return parent
        if '.' in pname:
            i = pname.rfind('.')
            pname = pname[:i]
            parent = sys.modules[pname]
            assert parent.__name__ == pname
            return parent
        return None

    def __find_head_package(self, parent, name):
        if '.' in name:
            i = name.find('.')
            head = name[:i]
            tail = name[i+1:]
        else:
            head = name
            tail = ""
        if parent:
            qname = "%s.%s" % (parent.__name__, head)
        else:
            qname = head
        q = self.__import_module(head, qname, parent)
        if q: return q, tail
        if parent:
            qname = head
            parent = None
            q = self.__import_module(head, qname, parent)
            if q: return q, tail
        raise ImportError, "No module named " + qname

    def __load_tail(self, q, tail):
        m = q
        while tail:
            i = tail.find('.')
            if i < 0: i = len(tail)
            head, tail = tail[:i], tail[i+1:]
            mname = "%s.%s" % (m.__name__, head)
            m = self.__import_module(head, mname, m)
            if not m:
                raise ImportError, "No module named " + mname
        return m

    def __ensure_fromlist(self, m, fromlist, recursive=0):
        for sub in fromlist:
            if sub == "*":
                if not recursive:
                    try:
                        all = m.__all__
                    except AttributeError:
                        pass
                    else:
                        self.__ensure_fromlist(m, all, 1)
                continue
            if sub != "*" and not hasattr(m, sub):
                subname = "%s.%s" % (m.__name__, sub)
                submod = self.__import_module(sub, subname, m)
                if not submod:
                    raise ImportError, "No module named " + subname

    def __import_module(self, partname, fqname, parent):
        try:
            return sys.modules[fqname]
        except KeyError:
            pass
        try:
            fp, pathname, stuff = imp.find_module(partname, parent and parent.__path__)
        except ImportError:
            return None
        try:
            m = imp.load_module(fqname, fp, pathname, stuff)
        finally:
            if fp: fp.close()
        if parent:
            setattr(parent, partname, m)
        return m

    # Replacement for reload()
    def _reload_hook(self, module):
        return reload(module)