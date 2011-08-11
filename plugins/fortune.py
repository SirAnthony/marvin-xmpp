import random

class Fortune:
    
    _marvinModule = True
    public = ['fortune', 'testm']

    def fortune(self, message):
        fortunes = ['The gene pool could use a little chlorine.',
                'Make it idiot proof and someone will make a better idiot.', 
                'He who laughs last thinks slowest.',
                'A flashlight is a case for holding dead batteries.', 
                'Lottery: A tax on people who are bad at math.',
                'I wouldnt be caught dead with a necrophiliac.', 
                'Consciousness: That annoying time between naps.',
                'I dont suffer from insanity.  I enjoy every minute of it.'
                'All of the books in the world contain no more information than is broadcast as video in a single large American city in a single year. Not all bits have equal value.',
                'And, for an instant, she stared directly into those soft blue eyes and knew, with an instinctive mammalian certainty, that the exceedingly rich were no longer even remotely human.',
                'Any sufficiently advanced technology is indistinguishable from magic.',
                'Bill Gates is a very rich man today... and do you want to know why? The answer is one word: versions.',
                'Champagne, if you are seeking the truth, is better than a lie detector. It encourages a man to be expansive, even reckless, while lie detectors are only a challenge to tell lies successfully.',
                'Civilization advances by extending the number of important operations which we can perform without thinking of them.',
                'Congress will pass a law restricting public comment on the Internet to individuals who have spent a minimum of one hour actually accomplishing a specific task while on line.',
                'Cyberspace. A consensual hallucination experienced daily by billions of legitimate operators, in every nation, by children being taught mathematical concepts.',
                'Do you realize if it werent for Edison we\'d be watching TV by candlelight?', 
                'Doing linear scans over an associative array is like trying to club someone to death with a loaded Uzi.', 
                'Dreaming in public is an important part of our job description, as science writers, but there are bad dreams as well as good dreams. We are dreamers, you see, but we are also realists, of a sort.', 
                'Everybody gets so much information all day long that they lose their common sense.',
                'For a successful technology, reality must take precedence over public relations, for Nature cannot be fooled.',
                'For my confirmation, I didnt get a watch and my first pair of long pants, like most Lutheran boys. I got a telescope. My mother thought it would make the best gift.',
                'For years I have been mourning and not for my dead, it is for this boy for whatever corner in my heart died when his childhood slid out of my arms.',
                'Gates is the ultimate programming machine. He believes everything can be defined, examined, reduced to essentials, and rearranged into a logical sequence that will achieve a particular goal.',
                'Getting information off the Internet is like taking a drink from a fire hydrant.', 
                'Globalization, as defined by rich people like us, is a very nice thing... you are talking about the Internet, you are talking about cell phones, you are talking about computers. This doesnt affect two-thirds of the people of the world.',
                'Humanity is acquiring all the right technology for all the wrong reasons.',
                'I am sorry to say that there is too much point to the wisecrack that life is extinct on other planets because their scientists were more advanced than ours.'
                ]

        quote = fortunes[random.randint(1,len(fortunes))]
        
        message.reply(quote)
        
    def testm(senlf, message):
        message.reply('It is a test module.')

