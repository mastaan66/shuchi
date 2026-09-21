rule EICAR_Test_File {
    meta:
        description = "Standard EICAR antivirus test file"
        author = "SHUCHI"
    strings:
        $eicar = "X5O!P%@AP[4\\PZX54(P^)7CC)7}$EICAR-STANDARD-ANTIVIRUS-TEST-FILE!$H+H*"
    condition:
        $eicar
}

rule Macro_VBA_OLE {
    meta:
        description = "Detects VBA macro in OLE files"
        author = "SHUCHI"
    strings:
        $vba = "AutoOpen" nocase
        $ole = "OLE2 Object" nocase
        $macro = "VBA_PROJECT" nocase
    condition:
        any of ($*) and uint16(0) == 0xD0CF
}

rule PDF_JS_Embed {
    meta:
        description = "Embedded JavaScript in PDF"
        author = "SHUCHI"
    strings:
        $js = "/JavaScript" nocase
        $action = "/Action" nocase
        $launch = "/Launch" nocase
        $pdf = "%PDF" nocase
    condition:
        $pdf and $js and ($action or $launch)
}

rule PDF_OpenAction {
    meta:
        description = "PDF with suspicious OpenAction"
        author = "SHUCHI"
    strings:
        $openaction = "/OpenAction" nocase
        $launch = "/Launch" nocase
        $java = "/JS" nocase
    condition:
        $openaction and ($launch or $java)
}

rule Office_External_Link {
    meta:
        description = "Office document with external link exploit pattern"
        author = "SHUCHI"
    strings:
        $hlink = "http://" nocase
        $auto = "Auto_Open" nocase
        $vba = "vbaProject.bin" nocase
    condition:
        any of ($*) and (uint32(0) == 0x504B0304 or uint32(0) == 0xD0CF11E0)
}

rule PowerShell_Encoded_Command {
    meta:
        description = "Encoded PowerShell command"
        author = "SHUCHI"
    strings:
        $ps = "powershell" nocase
        $enc = "-EncodedCommand" nocase
        $b64 = /[A-Za-z0-9+\/]{50,}={0,2}/
    condition:
        $ps and $enc and $b64
}

rule Shellcode_HEX_Pattern {
    meta:
        description = "Common shellcode hex patterns"
        author = "SHUCHI"
    strings:
        $hex1 = { 31 C0 31 DB 31 CC }
        $hex2 = { 50 6A 01 5E }
        $hex3 = { EB ?? 8B EC 83 E4 F8 }
        $hex4 = { 6A 40 68 00 30 00 00 6A 14 }
    condition:
        any of ($hex*)
}

rule OLE_Embedded_Obj {
    meta:
        description = "OLE embedded object with suspicious patterns"
        author = "SHUCHI"
    strings:
        $obj = "Embedded Object" nocase
        $cmd = "cmd.exe" nocase
        $exe = "\\.exe" nocase
    condition:
        $obj and ($cmd or $exe)
}

rule DDE_Exec_Exploit {
    meta:
        description = "DDE dynamic data exchange exploit pattern"
        author = "SHUCHI"
    strings:
        $dde = "DDE" nocase
        $exec = "exec" nocase
        $cmd = "cmd" nocase
    condition:
        $dde and $exec and $cmd and (uint32(0) == 0xD0CF11E0)
}

rule Malformed_Zip {
    meta:
        description = "Malformed ZIP archive header"
        author = "SHUCHI"
    strings:
        $zip = "PK" nocase
    condition:
        $zip and filesize < 100
}

rule Excel_External_Link {
    meta:
        description = "Excel external link formula"
        author = "SHUCHI"
    strings:
        $xl = "xl/" nocase
        $link = "externalLink" nocase
        $formula = "=" nocase
    condition:
        $xl and $link and $formula and uint32(0) == 0x504B0304
}

rule Word_Macro_Project {
    meta:
        description = "Word VBA macro project binary"
        author = "SHUCHI"
    strings:
        $vba = "VBA" nocase
        $proj = "Project" nocase
        $bin = "bin" nocase
    condition:
        $vba and $proj and $bin and uint32(0) == 0xD0CF11E0
}

rule PDF_Exploit_Obj {
    meta:
        description = "Suspicious PDF object exploit"
        author = "SHUCHI"
    strings:
        $obj = "/Obj" nocase
        $exec = "/Exec" nocase
        $filter = "/Filter" nocase
    condition:
        $obj and $exec and $filter
}

rule HTML_Meta_Refresh {
    meta:
        description = "HTML meta refresh redirect"
        author = "SHUCHI"
    strings:
        $meta = "<meta" nocase
        $refresh = "http-equiv=\"refresh\"" nocase
        $url = "url=" nocase
    condition:
        $meta and $refresh and $url
}

rule Base64_Payload {
    meta:
        description = "Large base64 encoded payload"
        author = "SHUCHI"
    strings:
        $b64 = /[A-Za-z0-9+\/]{50,}={0,2}/
    condition:
        $b64 and filesize > 1000
}

rule RTF_Control_Word_Exploit {
    meta:
        description = "RTF exploit control word"
        author = "SHUCHI"
    strings:
        $rtf = "{\\rtf" nocase
        $writes = "Write" nocase
        $shell = "shell" nocase
    condition:
        $rtf and ($writes or $shell)
}

rule Reg_Add_Startup {
    meta:
        description = "Registry add startup key"
        author = "SHUCHI"
    strings:
        $reg = "HKLM" nocase
        $startup = "Run" nocase
        $value = "reg add" nocase
    condition:
        all of ($*)
}

rule WMI_Command {
    meta:
        description = "WMI command pattern"
        author = "SHUCHI"
    strings:
        $wmi = "wmic" nocase
        $process = "process call create" nocase
    condition:
        $wmi and $process
}

rule Download_Exec {
    meta:
        description = "Download and execute pattern"
        author = "SHUCHI"
    strings:
        $url = "http://" nocase
        $down = "download" nocase
        $exec = "execute" nocase
    condition:
        $down and $exec and $url
}

rule PDF_Image_Obj {
    meta:
        description = "PDF with image object exploit"
        author = "SHUCHI"
    strings:
        $pdf = "%PDF" nocase
        $img = "/Image" nocase
        $filter = "/DCTDecode" nocase
    condition:
        $pdf and $img and $filter
}

rule Suspicious_Content_Types {
    meta:
        description = "Suspicious content types in OLE"
        author = "SHUCHI"
    strings:
        $ole = "OLE" nocase
        $type = "Content_Types" nocase
        $xml = "<?xml" nocase
    condition:
        $ole and $type and $xml and uint32(0) == 0xD0CF11E0
}

rule Office_External_Macro {
    meta:
        description = "Office external macro reference"
        author = "SHUCHI"
    strings:
        $ext = "vbaProject.bin" nocase
        $link = "external" nocase
        $office_word = "word" nocase
        $office_excel = "excel" nocase
        $office_ppt = "powerpoint" nocase
    condition:
        $ext and $link and any of ($office_*)
}

rule PDF_Unknown_Obj {
    meta:
        description = "PDF with unknown suspicious object"
        author = "SHUCHI"
    strings:
        $pdf = "%PDF" nocase
        $unknown = "/ObjStm" nocase
        $large = /Size\s+\d{5,}/ nocase
    condition:
        $pdf and $unknown and $large
}

rule Excel_4_0_Macro {
    meta:
        description = "Excel 4.0 macro (XLM)"
        author = "SHUCHI"
    strings:
        $xl = "xl/" nocase
        $xml = "/xl/xml" nocase
        $macro = "vbaProject" nocase
    condition:
        $xl and $xml and $macro and uint32(0) == 0x504B0304
}

rule Zip_Polyglot {
    meta:
        description = "Possible ZIP polyglot file"
        author = "SHUCHI"
    strings:
        $zip = "PK" nocase
        $exe = "MZ" nocase
    condition:
        $zip and $exe and filesize < 500000
}

rule Document_Recovery {
    meta:
        description = "Document recovery exploit pattern"
        author = "SHUCHI"
    strings:
        $repair = "Repair" nocase
        $orig = "Original" nocase
        $temp = "Temp" nocase
    condition:
        any of ($*) and filesize < 5000
}

rule Null_Byte_Injection {
    meta:
        description = "Null byte injection pattern"
        author = "SHUCHI"
    strings:
        $null = "%00" nocase
        $null2 = "\x00" nocase
    condition:
        $null or $null2
}

rule OLE_Compound_File {
    meta:
        description = "OLE compound file with suspicious stream"
        author = "SHUCHI"
    strings:
        $dcf = "Donald E. Knuth" nocase
        $stream = "WordDocument" nocase
    condition:
        $dcf and $stream
}

rule Script_Injection {
    meta:
        description = "Script injection in document"
        author = "SHUCHI"
    strings:
        $script = "<script" nocase
        $vbs = "vbscript" nocase
        $mshta = "mshta" nocase
    condition:
        any of ($*) and filesize > 10000
}
