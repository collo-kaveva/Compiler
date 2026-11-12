# Context-Free Grammar for a Simple Variable Declaration Language

A context-free grammar for a small variable declaration language. It accepts one or more declarations, such as:

```
int x;
float total;
int count = 10;
int total = x + 10;
```

## Grammar G = (N, T, P, S)

**Start symbol:** S = `<program>`

**Non-terminals:** N = { `<program>`, `<decl>`, `<type>`, `<init>`, `<expr>`, `<term>` }

**Terminals:** T = { `int`, `float`, `id`, `number`, `=`, `+`, `;` }

**Productions P:**

```
1.  <program> → <decl> <program> | <decl>
2.  <decl>    → <type> id <init> ;
3.  <type>    → int | float
4.  <init>    → = <expr> | ε
5.  <expr>    → <expr> + <term> | <term>
6.  <term>    → id | number
```

- Rule 1 lets the input contain one or more declarations in a row.
- Rule 5 allows any number of `+` terms: `x`, `x + 10`, `a + b + 1`.

### Token conventions

- `id` is an identifier token (e.g. `x`, `total`, `count`).
- `number` is a numeric literal token (e.g. `10`).
- `int` and `float` are reserved keywords and are not treated as `id`.
- `ε` denotes the empty string, so `<init> → ε` makes initialization optional.

## Sample Derivations (leftmost)

`int x;`
```
<program> ⇒ <decl> ⇒ <type> id <init> ; ⇒ int id <init> ; ⇒ int id ;
```

`float total;`
```
<program> ⇒ <decl> ⇒ <type> id <init> ; ⇒ float id <init> ; ⇒ float id ;
```

`int count = 10;`
```
<program> ⇒ <decl> ⇒ <type> id <init> ; ⇒ int id <init> ; ⇒ int id = <expr> ;
          ⇒ int id = <term> ; ⇒ int id = number ;
```

`int total = x + 10;`
```
<program> ⇒ <decl> ⇒ <type> id <init> ; ⇒ int id <init> ; ⇒ int id = <expr> ;
          ⇒ int id = <expr> + <term> ; ⇒ int id = <term> + <term> ;
          ⇒ int id = id + <term> ; ⇒ int id = id + number ;
```

## Rejected Inputs

| Input | Result | Reason |
|---|---|---|
| `= x;` | Rejected | `<decl>` must start with `<type>` |
| `int = 10;` | Rejected | `id` is required after `<type>` |
| `int x` | Rejected | `;` is mandatory |
| `int x =;` | Rejected | `<init> → = <expr>` needs a non-empty `<expr>` |
| `int x + 10;` | Rejected | `+` is only allowed inside `<expr>`, which follows `=` |

## Worked Example: Which Rule Is Violated?

Consider a tiny assignment language:

```
<stmt> → id = <expr> ;
<expr> → <expr> + <term> | <term>
<term> → id | number
```

Valid: `total = price + tax ;` and `x = 10 ;`

| Invalid statement | Rule violated | Why |
|---|---|---|
| `= x 10 ;` | `<stmt> → id = <expr> ;` | A statement must start with `id`, but this one starts with `=`. `x 10` also breaks `<expr> → <expr> + <term> \| <term>`: two terms need a `+` between them. |
| `total price + tax ;` | `<stmt> → id = <expr> ;` | The `=` after `total` is missing. `price + tax` on its own is a valid `<expr>`. |

Both statements contain only valid tokens (`id`, `=`, `number`, `+`, `;`), so the lexer accepts them. They are syntax errors (a rule is broken), not lexical errors (an invalid token).
