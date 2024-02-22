These are scripts that I have written and used in my role as Discovery and Systems Manager at Solent University Library. I am a librarian who does some scripting for his job; I AM NOT A PROFESSIONAL SOFTWARE DEVELOPER, so the scripts are certainly unsophisticated and probably flawed in some way. However, they have all been used many times at Solent University, so it struck me that they may be of use to others. Indeed, the fact that they were written by an amateur may make them of more use to other amateur scripters than professional code - they may be more comprehensible.

That said, you use these scripts at your own risk. I have edited some of them without then testing - I'll do that when I have a use case - so errors may have crept in. You'll need to know Python basics before using them (and have Python installed), and you should read through the code to make sure it does what you want. You should also check out the Alma API docs on the ExLibris Developer Zone. 

There is a main file, alma.py, that serves as a module file. In here I include small functions that I use repeatedly. When I want to do a specific project, I call this file with the following lines of code in my project script:

import sys
sys.path.append('C:\Users\clarkj\OneDrive - Solent University\PythonModules')
import alma

My work laptop is locked down, so I can't add the directory where I store this file to the path permanently; I have to do it for every script using the first two lines above. Then I just import the alma module, and call the functions as with a normal module, e.g., alma.update_holding(mms_id, hol_id, xml_in_bytes).

The functions and how they work are, I think, all self explanatory. So instead of creating separate documentation, I suggest you take a look at the code itself to identify potentially useful functions. There are comments in there to elucidate certain bits. Not that you might need to edit the api_base balue to suit your own context. For security, the script prompts for the API key each time it is run. 
