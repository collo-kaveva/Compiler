# Context-Free Grammar for a Simple Variable Declaration Language

A small CFG for a Compiler Construction class activity. It accepts declarations such as:

```
int x;
float total;
int count = 10;
int total = x + 10;
```

## Grammar G = (N, T, P, S)

**Start symbol:** S = `Decl`

**Non-terminals:** N = { `Decl`, `Type`, `Init`, `Expr` }

**Terminals:** T = { `int`, `float`, `id`, `num`, `=`, `+`, `;` }

**Productions P:**

```
1.  Decl → Type id Init ;
2.  Type → int
3.  Type → float
4.  Init → = Expr
5.  Init → ε
6.  Expr → num
7.  Expr → id + num
```

### Token conventions

- `id` is an identifier token (e.g. `x`, `total`, `count`).
- `num` is a numeric literal token (e.g. `10`).
- `int` and `float` are reserved keywords and are not treated as `id`.
- `ε` denotes the empty string, so `Init → ε` makes initialization optional.

## Sample Derivations (leftmost)

`int x;`
```
Decl ⇒ Type id Init ; ⇒ int id Init ; ⇒ int id ;
```

`float total;`
```
Decl ⇒ Type id Init ; ⇒ float id Init ; ⇒ float id ;
```

`int count = 10;`
```
Decl ⇒ Type id Init ; ⇒ int id Init ; ⇒ int id = Expr ; ⇒ int id = num ;
```

`int total = x + 10;`
```
Decl ⇒ Type id Init ; ⇒ int id Init ; ⇒ int id = Expr ; ⇒ int id = id + num ;
```

## Rejected Inputs

| Input | Result | Reason |
|---|---|---|
| `= x;` | Rejected | `Decl` must start with `Type` |
| `int = 10;` | Rejected | `id` is required after `Type` |
| `int x` | Rejected | `;` is mandatory |
| `int x =;` | Rejected | `Init → = Expr` needs a non-empty `Expr` |
| `int x + 10;` | Rejected | `+` is only allowed inside `Expr`, which follows `=` |

## Why It Is Deterministic (LL(1))

One lookahead token decides every choice:

- `Type`: `int` or `float`
- `Init`: `=` selects `= Expr`; `;` selects `ε`
- `Expr`: `num` selects `num`; `id` selects `id + num`
