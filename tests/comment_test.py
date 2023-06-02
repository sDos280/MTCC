import Parser.mtcc_lexer
import Parser.mtcc_token

lexer = Parser.mtcc_lexer.Lexer('comment.c')
lexer.lex()

for index, comment in enumerate(lexer.comments):
    print(f"comment {index}: Lexer: ")
    print(comment.string)
