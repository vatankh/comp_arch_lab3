; Ask for the user's name
MOV A, 87        ; W
WRITE A
MOV A, 104       ; h
WRITE A
MOV A, 97        ; a
WRITE A
MOV A, 116       ; t
WRITE A
MOV A, 32        ; (space)
WRITE A
MOV A, 105       ; i
WRITE A
MOV A, 115       ; s
WRITE A
MOV A, 32        ; (space)
WRITE A
MOV A, 121       ; y
WRITE A
MOV A, 111       ; o
WRITE A
MOV A, 117       ; u
WRITE A
MOV A, 114       ; r
WRITE A
MOV A, 32        ; (space)
WRITE A
MOV A, 110       ; n
WRITE A
MOV A, 97        ; a
WRITE A
MOV A, 109       ; m
WRITE A
MOV A, 101       ; e
WRITE A
MOV A, 63        ; ?
WRITE A
MOV A, 10        ; newline after the question
WRITE A

; Start of input reading loop
MOV B, 0         ; Initialize memory index in B

READ_LOOP:
READ A           ; Read a character from input
CMP A, 0        ; Check if the input is a newline (ASCII 10)
JZ PRINT_GREETING; If newline, jump to print the greeting

MOV [B], A       ; Store the input character at memory[B]
WRITE A          ; Echo the input character back
INC B            ; Move to the next memory location
JMP READ_LOOP    ; Continue reading the next character

MOV [B], 0       ; Store a null terminator at memory[B]


; Printing the greeting "Hello, " and the user's name
PRINT_GREETING:
MOV A, 10        ; Newline after input
WRITE A
MOV A, 72        ; H
WRITE A
MOV A, 101       ; e
WRITE A
MOV A, 108       ; l
WRITE A
WRITE A          ; l
MOV A, 111       ; o
WRITE A
MOV A, 44        ; ,
WRITE A
MOV A, 32        ; (space)
WRITE A

; Print user's name from memory
MOV C, 0         ; Initialize memory index in C for printing

PRINT_NAME_LOOP:
MOV A, [C]       ; Load character from memory[C]
CMP A, 0         ; Check if it's the end of the name (stored as null)
JZ PRINT_DONE    ; If end, jump to finish

WRITE A          ; Print the character
INC C            ; Move to the next memory location
JMP PRINT_NAME_LOOP ; Loop to print the next character

PRINT_DONE:
MOV A, 33        ; !
WRITE A

HALT
