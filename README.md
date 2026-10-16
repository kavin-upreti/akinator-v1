# Small Akinator for fun
A small akinator game with custom data (I made it using my friends' data)
Not too advanced (yet)

questions.csv:
column means the column pertaining to the one for that question from fake.csv (fake.csv because i originally had fake data)
text is the text of the question
operator is what to check - does it have to be equal, not equal, less/greater than (/equal to), or "in", or "!in" (not in)
compareto means check against which value with the operator
sureness means how much score change does that question do

in text:
$ABC~DEF~GHI$ means that you can send either of the 3 texts, but operator and compareto should have those many options too
like if it selects ABC, then it will select the first from operator and first from compareto too.
in compareto, a|b|c means answer is either a or b or c