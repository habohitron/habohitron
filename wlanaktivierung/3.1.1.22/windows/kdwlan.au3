#NoTrayIcon
#Region ;**** Directives created by AutoIt3Wrapper_GUI ****
#AutoIt3Wrapper_Icon=habo.ico
#AutoIt3Wrapper_Outfile=kdwlan.exe
#AutoIt3Wrapper_Res_Fileversion=1.0.0
#AutoIt3Wrapper_Res_LegalCopyright=flipflop
#AutoIt3Wrapper_Res_Language=1031
#EndRegion ;**** Directives created by AutoIt3Wrapper_GUI ****
#include <GUIConstantsEx.au3>
#include <EditConstants.au3>

Opt("MustDeclareVars", 1)
Opt("GUIOnEventMode", 1)

Const $WIDTH = 200
Const $HEIGHT = 140
Const $INPUT_OFFSET = 2
Const $S_OK = 0

Local $hwnd, $winhttp
Local $inIp, $inUser, $inPass, $buActivate

$winhttp = ObjCreate("WinHttp.WinHttpRequest.5.1")
If $winhttp == 0 Then
	MsgBox(48, "Error", "Dieses Programm benötigt die Komponente WinHttp.WinHttpRequest.5.1, welche Sie nicht besitzen")
	Exit
EndIf

$hwnd = GUICreate("KD-Wlan", $WIDTH, $HEIGHT)
GUISetOnEvent($GUI_EVENT_CLOSE, "_EXIT")
GUICtrlCreateLabel("Router-Ip:", 20, 10 + $INPUT_OFFSET, 60)
GUICtrlCreateLabel("Benutzer:", 20, 40 + $INPUT_OFFSET, 60)
GUICtrlCreateLabel("Passwort:", 20, 70 + $INPUT_OFFSET, 60)
$inIp = GUICtrlCreateInput("192.168.0.1", 85, 10, 100, 20)
$inUser = GUICtrlCreateInput("admin", 85, 40, 100, 20)
$inPass = GUICtrlCreateInput("", 85, 70, 100, 20, BitOR($ES_LEFT, $ES_AUTOHSCROLL, $ES_PASSWORD))
$buActivate = GUICtrlCreateButton("Aktiviere", 85, 100, 100, 30)
GUICtrlSetState($inPass, $GUI_FOCUS)
GUICtrlSetOnEvent($buActivate, "_ACTIVATE")

GUISetState(@SW_SHOW, $hwnd)
While True
	Sleep(1000)
WEnd

Func HttpGet($url)
	If $winhttp.Open("GET", $url, False) <> $S_OK Then
		Return -1
	EndIf
	If $winhttp.Send() <> $S_OK Then
		Return -1
	EndIf
	Return $winhttp.ResponseText
EndFunc   ;==>HttpGet

Func HttpPost($url, $data)
	If $winhttp.Open("POST", $url, False) <> $S_OK Then
		Return -1
	EndIf
	If $winhttp.Send($data) <> $S_OK Then
		Return -1
	EndIf
	Return $winhttp.ResponseText
EndFunc   ;==>HttpPost

Func ActivateWlan($host, $user, $pass)
	If Ping($host, 1000) == 0 Then
		Return "Host nicht erreichbar"
	EndIf
	If HttpGet("http://" & $host & "/login.asp") == -1 Then
		Return "Login nicht erreichbar"
	EndIf
	If HttpPost("http://" & $host & "/goform/login", "user=" & $user & "&pws=" & $pass) == -1 Then
		Return "Login fehlgeschlagen"
	EndIf
	If HttpPost("http://" & $host & "/goform/Wls", "dir=admin/&file=wireless&wireless=1") == -1 Then
		Return "Aktivierungsanfrage fehlgeschlagen"
	EndIf
	If HttpGet("http://" & $host & "/goform/logout") == -1 Then
		Return "Logout fehlgeschlagen"
	EndIf
	Return ""
EndFunc   ;==>ActivateWlan

Func _EXIT()
	Exit
EndFunc   ;==>_EXIT

Func _ACTIVATE()
	Local $host, $user, $pass, $error

	GUICtrlSetState($buActivate, $GUI_DISABLE)
	$host = GUICtrlRead($inIp)
	$user = GUICtrlRead($inUser)
	$pass = GUICtrlRead($inPass)
	$error = ActivateWlan($host, $user, $pass)
	If $error <> "" Then
		MsgBox(48, "Error", $error, 0, $hwnd)
	EndIf
	GUICtrlSetState($buActivate, $GUI_ENABLE)
EndFunc   ;==>_ACTIVATE