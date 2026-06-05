#Requires AutoHotkey v2.0
#SingleInstance Force

; ---------------------------
; CONFIG
; ---------------------------
buffer := ""
maxLen := 50  ; how many recent characters to track

; Define triggers and replacements here
triggers := { 
    ":test": "This is typed like a human, not pasted.",
    ":sig":  "Best regards, Nix"
}

; ---------------------------
; HUMAN TYPING FUNCTION
; ---------------------------
HumanType(text) {
    for char in StrSplit(text) {
        Send char
        Sleep Random(25, 90)   ; human-like delay per character
        if (Random(1,100) <= 5) ; occasional micro-pause
            Sleep Random(120, 300)
    }
}

; ---------------------------
; TRACK KEYPRESSES
; ---------------------------
Track(char) {
    global buffer, maxLen, triggers

    buffer .= char
    if (StrLen(buffer) > maxLen)
        buffer := SubStr(buffer, -maxLen)

    ; Check all triggers
    for key, val in triggers {
        if (SubStr(buffer, -StrLen(key) + 1) = key) {
            ; Trigger matched
            buffer := ""
            Send "{Backspace " StrLen(key) "}"
            HumanType(val)
        }
    }
}

; ---------------------------
; DYNAMIC HOTKEYS FOR ALL CHARACTERS
; ---------------------------
chars := "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789`~!@#$%^&*()-_=+[]{}|\;:',.<>/? "
for index, c in StrSplit(chars)
{
    ~*%c%::Track(c)  ; Correct v2 syntax
}

; Add space separately
~*Space::Track(" ")
~*Enter::Track("`n")
