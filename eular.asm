; Initialize registers
MOV A, 1          ; A will hold the current number (starting from 1)
MOV B, 0          ; B will hold the sum of multiples
MOV C, 1000       ; C holds the upper limit (1000)
MOV D, 3          ; D holds the value 3 for divisibility check
MOV E, 5          ; E holds the value 5 for divisibility check

; Write initial state
WRITE A           ; Output the current number (A)
WRITE B           ; Output the initial sum (B)

MAIN_LOOP:
    ; Check if A >= 1000
    CMP A, C      ; Compare current number (A) with 1000
    JZ END_LOOP   ; If A >= 1000, jump to end the loop

    ; Check if A is divisible by 3
    MOV F, A      ; Copy A to F
    DIV F, D      ; Divide F by 3
    CMP F, 0      ; Check if the remainder is 0 (divisible by 3)
    JZ ADD_TO_SUM ; If divisible by 3, jump to add to sum

    ; Check if A is divisible by 5
    MOV F, A      ; Copy A to F
    DIV F, E      ; Divide F by 5
    CMP F, 0      ; Check if the remainder is 0 (divisible by 5)
    JZ ADD_TO_SUM ; If divisible by 5, jump to add to sum

    ; If not divisible by 3 or 5, continue the loop
    INC A         ; Increment A to check the next number
    JMP MAIN_LOOP ; Repeat the loop

ADD_TO_SUM:
    ADD B, A      ; Add the current number (A) to the sum (B)
    INC A         ; Increment A to check the next number
    JMP MAIN_LOOP ; Repeat the loop

END_LOOP:
    ; Print the result (sum of multiples)
    MOV A, B      ; Move the result (B) to A for output
    WRITE_NUM A       ; Output the final sum
    HALT          ; Stop the program
