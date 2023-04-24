#include <stdio.h>

int main() {
    printf("\\\'\n");    // single quote
    printf("\\\"\n");    // double quote
    printf("\\?\n");     // question mark
    printf("\\\\\n");    // backslash
    printf("\\a\n");     // alert (bell) character
    printf("\\b\n");     // backspace
    printf("\\f\n");     // form feed
    printf("\\n\n");     // newline (line feed)
    printf("\\r\n");     // carriage return
    printf("\\t\n");     // horizontal tab
    printf("\\v\n");     // vertical tab
    printf("\\0\n");     // null character
    // printf("\\x41\n");   // hexadecimal representation of a character (here 'A')

    return 0;
}
