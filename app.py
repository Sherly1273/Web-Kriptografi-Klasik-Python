import base64, struct
from math import gcd, isqrt
from flask import Flask, render_template, request, jsonify
from sympy import Matrix

app = Flask(__name__)
MAGIC = b"CRY1"

def L(d):
    return [b - 65 for b in d.upper() if 65 <= b <= 90]


def S(v):
    return bytes(x + 65 for x in v)


def K(key):
    k = L(key.encode())
    if not k:
        raise ValueError("Kunci harus mengandung huruf A-Z")
    return k


def vigenere(d, key, dec):
    p, k, s = L(d), K(key), -1 if dec else 1
    return S((c + s * k[i % len(k)]) % 26 for i, c in enumerate(p))


def autokey(d, key, dec):
    p, k = L(d), K(key)
    if not dec:
        ks = k + p
        return S((c + ks[i]) % 26 for i, c in enumerate(p))
    ks, out = list(k), []
    for i, c in enumerate(p):
        x = (c - ks[i]) % 26
        out.append(x)
        ks.append(x)
    return S(out)


def extended(d, key, dec):
    kb = key.encode()
    if not kb:
        raise ValueError("Kunci tidak boleh kosong")
    s = -1 if dec else 1
    return bytes((b + s * kb[i % len(kb)]) % 256 for i, b in enumerate(d))


def playfair(d, key, dec):
    sq = []
    for c in K(key) + list(range(26)):
        c = 8 if c == 9 else c
        if c not in sq:
            sq.append(c)
    pos = {c: divmod(i, 5) for i, c in enumerate(sq)}
    p = [8 if c == 9 else c for c in L(d)]
    if not dec:
        out, i = [], 0
        while i < len(p):
            a = p[i]
            b = p[i + 1] if i + 1 < len(p) else 23
            if a == b:
                b = 23
                i += 1
            else:
                i += 2
            out += [a, b]
        p = out
    elif len(p) % 2:
        raise ValueError("Panjang cipherteks Playfair harus genap")
    s, res = (-1 if dec else 1), []
    for i in range(0, len(p), 2):
        (r1, c1), (r2, c2) = pos[p[i]], pos[p[i + 1]]
        if r1 == r2:
            c1, c2 = (c1 + s) % 5, (c2 + s) % 5
        elif c1 == c2:
            r1, r2 = (r1 + s) % 5, (r2 + s) % 5
        else:
            c1, c2 = c2, c1
        res += [sq[r1 * 5 + c1], sq[r2 * 5 + c2]]
    return S(res)


def affine(d, key, dec):
    try:
        a, b = [int(x) for x in key.replace(" ", "").split(",")]
    except Exception:
        raise ValueError("Kunci Affine harus berformat a,b")
    if gcd(a, 26) != 1:
        raise ValueError("a harus koprima dengan 26")
    ai = pow(a, -1, 26)
    return S(((ai * (c - b)) if dec else (a * c + b)) % 26 for c in L(d))


def hill(d, key, dec):
    try:
        nums = [int(x) for x in key.replace(",", " ").split()]
    except Exception:
        raise ValueError("Kunci Hill berisi angka")
    n = isqrt(len(nums))
    if n < 2 or n * n != len(nums):
        raise ValueError("Jumlah angka kunci harus kuadrat sempurna (4, 9, ...)")
    M = Matrix(n, n, nums)
    if gcd(int(M.det()) % 26, 26) != 1:
        raise ValueError("Determinan kunci tidak punya invers mod 26")
    if dec:
        M = M.inv_mod(26)
    p = L(d)
    if dec and len(p) % n:
        raise ValueError("Panjang cipherteks harus kelipatan %d" % n)
    p += [23] * (-len(p) % n)
    out = []
    for i in range(0, len(p), n):
        out += [int(x) % 26 for x in M * Matrix(p[i : i + n])]
    return S(out)


def _perm(n, key):
    cols = len(key)
    order = sorted(range(cols), key=lambda i: (key[i], i))
    return [i for c in order for i in range(c, n, cols)]


def superenc(d, key, dec):
    kb = key.encode()
    if not kb:
        raise ValueError("Kunci tidak boleh kosong")
    if not dec:
        e = extended(d, key, False)
        pm = _perm(len(e), kb)
        return bytes(e[i] for i in pm)
    pm = _perm(len(d), kb)
    t = bytearray(len(d))
    for j, i in enumerate(pm):
        t[i] = d[j]
    return extended(bytes(t), key, True)


ROTORS = [  # (kabel, notch) Enigma I
    ("EKMFLGDQVZNTOWYHXUSPAIBRCJ", "Q"),
    ("AJDKSIRUXBLHWTMCQGZNPYFVOE", "E"),
    ("BDFHJLCPRTXVZNYEIWGAKMUSQO", "V"),
]
REFLECTOR_B = "YRUHQSLDPXNGOKMIEBFZCWVJAT"


def enigma(d, key, dec):
    """Enigma I (rotor I-II-III, reflektor B). Kunci: 'ABC' atau 'ABC AB CD'
    (posisi awal rotor kiri-tengah-kanan, lalu pasangan plugboard)."""
    parts = key.upper().split()
    if not parts or len(parts[0]) != 3 or not parts[0].isalpha():
        raise ValueError("Kunci Enigma: 3 huruf posisi rotor, mis. ABC")
    pos = [ord(c) - 65 for c in parts[0]]
    plug = list(range(26))
    for pr in parts[1:]:
        if len(pr) != 2 or not pr.isalpha() or pr[0] == pr[1]:
            raise ValueError("Plugboard berupa pasangan 2 huruf berbeda, mis. AB CD")
        a, b = ord(pr[0]) - 65, ord(pr[1]) - 65
        if plug[a] != a or plug[b] != b:
            raise ValueError("Huruf plugboard tidak boleh dipakai dua kali")
        plug[a], plug[b] = b, a
    fwd = [[ord(c) - 65 for c in w] for w, _ in ROTORS]
    inv = [[w.index(chr(65 + i)) for i in range(26)] for w, _ in ROTORS]
    ref = [ord(c) - 65 for c in REFLECTOR_B]
    notch = [ord(n) - 65 for _, n in ROTORS]
    out = []
    for c in L(d):
        # putar rotor (termasuk double-stepping)
        if pos[1] == notch[1]:
            pos[0] = (pos[0] + 1) % 26
            pos[1] = (pos[1] + 1) % 26
        elif pos[2] == notch[2]:
            pos[1] = (pos[1] + 1) % 26
        pos[2] = (pos[2] + 1) % 26
        c = plug[c]
        for i in (2, 1, 0):
            c = (fwd[i][(c + pos[i]) % 26] - pos[i]) % 26
        c = ref[c]
        for i in (0, 1, 2):
            c = (inv[i][(c + pos[i]) % 26] - pos[i]) % 26
        out.append(plug[c])
    return S(out)  # enkripsi dan dekripsi sama (resiprokal)


CIPHERS = {
    "vigenere": ("Vigenere Standard (26 huruf)", vigenere),
    "autokey": ("Auto-Key Vigenere (26 huruf)", autokey),
    "extended": ("Extended Vigenere (256 ASCII)", extended),
    "playfair": ("Playfair (26 huruf)", playfair),
    "affine": ("Affine (26 huruf)", affine),
    "hill": ("Hill (26 huruf)", hill),
    "enigma": ("Enigma (26 huruf)", enigma),
    "super": ("Super Enkripsi (Ext. Vigenere + Transposisi Kolom)", superenc),
}

b64 = lambda b: base64.b64encode(b).decode()


@app.route("/")
def index():
    return render_template("index.html", ciphers=CIPHERS)


@app.route("/api/process", methods=["POST"])
def process():
    f = request.form
    try:
        fn = CIPHERS[f["cipher"]][1]
        dec = f["mode"] == "dec"
        key = f.get("key", "")
        up = request.files.get("file")
        name = ""
        if f.get("source") == "file" and up:
            raw, name = up.read(), up.filename
        else:
            raw = f.get("text", "").encode()
        if dec:
            if f.get("source") == "file" and up:
                if raw.startswith(MAGIC):
                    n = struct.unpack(">H", raw[4:6])[0]
                    name = raw[6 : 6 + n].decode()
                    raw = raw[6 + n :]
                else:
                    name = ""
            else:
                raw = base64.b64decode("".join(f.get("text", "").split()))
            inp = raw
            out = fn(raw, key, True)
            dl = out
            dlname = name or "plainteks.bin"
        else:
            inp = raw
            out = fn(raw, key, False)
            dl = MAGIC + struct.pack(">H", len(name.encode())) + name.encode() + out
            dlname = "cipherteks.dat"
        return jsonify(
            ok=True,
            in_b64=b64(inp),
            out_b64=b64(out),
            preview=out.decode("utf-8", "replace")[:2000],
            dl_b64=b64(dl),
            dl_name=dlname,
        )
    except Exception as e:
        return jsonify(ok=False, error=str(e)), 400


if __name__ == "__main__":
    app.run(debug=True)
