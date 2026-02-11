# mtclone

**Gerenciador de APK open-source** — descompila, edita, recompila e assina APKs de forma simples via linha de comando.

> Sem telemetria. Sem chamadas de rede ocultas. 100% offline (exceto download inicial das ferramentas).

---

## Requisitos

- **Python 3.11+**
- **Java JDK 11+** (necessário para apktool e uber-apk-signer)

## Instalação

```bash
# Clone o repositório
git clone https://github.com/seu-usuario/mtclone.git
cd mtclone

# Instale
pip install .

# Ou em modo de desenvolvimento
pip install -e .
```

## Uso

### Descompilar APK

```bash
mtclone decode meu_app.apk
# Saída: ./meu_app/

mtclone decode meu_app.apk -o pasta_destino
# Saída: ./pasta_destino/
```

### Recompilar APK (build + align + sign)

```bash
mtclone build ./meu_app/
# Saída: meu_app_mod.apk (alinhado e assinado)

mtclone build ./meu_app/ -o nome_custom.apk
```

### Assinar APK

```bash
mtclone sign meu_app.apk
```

### Alinhar APK

```bash
mtclone align meu_app.apk
```

### Logs detalhados

```bash
mtclone -v decode meu_app.apk
```

---

## Exemplo: Patch de Smali (Coins)

Um caso de uso comum é modificar valores em jogos para fins de estudo. Aqui está um exemplo didático de como alterar o valor de coins em código smali:

### 1. Descompilar

```bash
mtclone decode jogo.apk
```

### 2. Localizar o campo de coins

Procure nos arquivos smali pelo campo que armazena coins:

```bash
# Buscar referências a "coins" nos arquivos smali
grep -r "coins" ./jogo/smali/ --include="*.smali"
```

Exemplo de resultado:

```
./jogo/smali/com/example/game/Player.smali:    .field private coins:I
./jogo/smali/com/example/game/Player.smali:    iget v0, p0, Lcom/example/game/Player;->coins:I
```

### 3. Editar o smali

Abra o arquivo `Player.smali` e localize o método que retorna os coins.
Altere o valor para um número fixo:

**Antes:**
```smali
.method public getCoins()I
    .locals 1
    iget v0, p0, Lcom/example/game/Player;->coins:I
    return v0
.end method
```

**Depois:**
```smali
.method public getCoins()I
    .locals 1
    # Valor original comentado:
    # iget v0, p0, Lcom/example/game/Player;->coins:I
    const v0, 0xF4240    # 1.000.000 em hexadecimal
    return v0
.end method
```

Ou, para modificar o valor inicial no construtor:

**Antes:**
```smali
.method public constructor <init>()V
    .locals 1
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    const/4 v0, 0x0
    iput v0, p0, Lcom/example/game/Player;->coins:I
    return-void
.end method
```

**Depois:**
```smali
.method public constructor <init>()V
    .locals 1
    invoke-direct {p0}, Ljava/lang/Object;-><init>()V
    const v0, 0x98968    # 625.000 coins iniciais
    iput v0, p0, Lcom/example/game/Player;->coins:I
    return-void
.end method
```

### 4. Recompilar

```bash
mtclone build ./jogo/
# Gera: jogo_mod.apk (alinhado + assinado)
```

### 5. Instalar

```bash
adb install -r jogo_mod.apk
```

---

## Referência rápida de Smali

| Tipo    | Smali    | Descrição                  |
|---------|----------|----------------------------|
| `int`   | `I`      | Inteiro 32-bit             |
| `long`  | `J`      | Inteiro 64-bit             |
| `float` | `F`      | Ponto flutuante 32-bit     |
| `bool`  | `Z`      | Booleano                   |
| `String`| `Ljava/lang/String;` | String        |

| Instrução       | O que faz                              |
|-----------------|----------------------------------------|
| `const v0, 0x..`| Carrega constante no registro          |
| `iget`          | Lê campo de instância                  |
| `iput`          | Escreve campo de instância             |
| `sget`          | Lê campo estático                      |
| `sput`          | Escreve campo estático                 |

---

## Ferramentas baixadas automaticamente

Na primeira execução, o mtclone baixa automaticamente:

| Ferramenta        | Fonte                                    |
|-------------------|------------------------------------------|
| apktool 2.9.3     | github.com/iBotPeaches/Apktool           |
| uber-apk-signer   | github.com/nicedayzhu/uber-apk-signer    |
| zipalign 34.0.0   | Android Build Tools (mirror)             |

Tudo fica em `~/.mtclone/tools/`.

## Estrutura do projeto

```
mtclone/
├── __init__.py
├── __main__.py          # CLI (argparse)
├── core/
│   ├── __init__.py
│   ├── apktool.py       # Wrapper subprocess para apktool
│   ├── signer.py        # Assinatura com uber-apk-signer
│   └── align.py         # Alinhamento com zipalign
└── utils/
    ├── __init__.py
    └── downloader.py    # Download automático de binários
```

## Licença

MIT — use, modifique e distribua livremente.
