import subprocess

def asrun(ascript):
  "Run the given AppleScript and return the standard output and error."

  osa = subprocess.Popen(['osascript', '-'],
                         stdin=subprocess.PIPE,
                         stdout=subprocess.PIPE)
  return osa.communicate(ascript)[0]

def asquote(astr):
  "Return the AppleScript equivalent of the given string."
  
  astr = astr.replace('"', '" & quote & "')
  return '"{}"'.format(astr)

subject = 'A new email'

body = '''This is the body of my "email."
I hope it comes out right.

Regards,
Dr. Drang
'''

ascript = '''
tell application "Mail"
  activate
  make new outgoing message with properties {{visible:true, subject:{0}, content:{1}}}
end tell
'''.format(asquote(subject), asquote(body))

ascript = '''
tell application "Google Chrome"
  make new window
  open location "file:///Users/andyreagan/work/2014/03-labMTsimple/test-inkscape.html"
  activate
  keystroke "p" using {option down, command down}
  delay 0.1
  tell menu button 1 of window 1
    click
    click menu item "Save as PDF..." of menu 1
  end tell
end tell
'''

asrun(ascript)

