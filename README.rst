======
Marvin
======

An xmpp chat bot with modular structure

About
======

Just another jabber bot. Why not?

Mision
------

Marvin was designed as a modular bot where all functionality provides by 
third-party modules. Core of bot it is just a loader for those plugins, and tool
which is make interaction between plugins and end users easier.

Bot core methods
------

Core of the bot have some methods for plugins management.
All core methods use ! mark at start.

!modules
  prints all loaded modules
!functions
  prints all available functions which is processed as commands
!aliases
  prints all commands aliases with command names near to aliases
!reload [modulename]
  loads (reloads) module if modulename passed. Reloads all modules from
  default pluggins directory otherwise.
!help [modulename]
  prints help for module modulename. If no argument passed prints general 
  help.

Functions
------

Functions is provided by modules. If function name presents of the string
beginning a chat phrase is recognised as a bot command.
For detail description of function creating look at the functions_ part of
the `Modules`_ section below.

Aliases
------

Aliases it is just short names for functions. Each function can have unlimited
count of aliases. Aliases begins with the % sign and recognises till the end of
the line (will be fixed in next releases). More about aliases creation you can
find in aliases_ part of `Modules`_ section below.

Help
------

Functions and modules help provides by modules but help mechanism realised in
core. To get module help you need to send '!help modulename' as command where
modulename it is module path name. To get function help you need to pass 'help'
as function parameter. To determine which module has this function and also get
module help you need to pass 'help module' to module function as parameter.


Modules
======

This section describes internal structure of Marvin modules

Base
------

Marvin module is a python class which have property ``_marvinModule`` set to
True (or equivalent). Also modules can have optional properties which is used
during module loading:

:public: A list of functions which is avaliable for usage for user.
:aliases: A dict of function aliases.
:depends: A module depends.

.. _functions:
Functions
------

Functions it is a module class methods. There are two types of functions 
availiable: public and private. Private functions are avaliable for use by
module itself while public functions are available for end-users through the
commands interface. To make function public you need to add its name to 
``public`` module list.

All public functions must accept Message_ object as first parameter. To send 
the result moduel may use Message object method.

.. _aliases:
Aliases
------

Aliases it is short names for functions. Aliases can be used anywhere in text
and reconised as command. To make command alias its name must be added as list
item of ``aliases`` dict of module class value with a key which is a function 
name.

.. _dependencies:
Module dependencies
------

Modules may have dependencies from another modules. To add dependence just add
python-style path to module (from bot main dir) in ``depends`` variable of the
module. Dependencies loads after subordinate module loaded (will be fixed).
When dependencies is loaded it is avaliable through ``depends`` variable of the
module. This variable provides an objects currently used in bot i.e. you gain
access to all module instance function and variables. 


Technical notes
======

Some additional technical information.

.. _message:
Message class
------

Message class have field described below.

type
  Type of the message.
form
  Message sender raw location (JID with resource).
user
  Message sender JID.
resource
  Message sender resource.
text
  Raw message text. It is highly recommended to use ctext instead.
ctext
  Message text which was been processed by core.
reply
  Function which modules can use to send messages to chat.

