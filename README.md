# Aplikasi Enkripsi dan Dekripsi (Python + Flask)

Aplikasi web untuk mengenkripsi dan mendekripsi pesan atau file dengan cipher klasik.
Dibuat untuk UTS Kriptografi.

## Cipher yang tersedia
1. Vigenere Standard (26 huruf)
2. Auto-Key Vigenere (26 huruf)
3. Extended Vigenere (256 karakter ASCII)
4. Playfair (26 huruf)
5. Affine (26 huruf)
6. Hill (26 huruf)
7. Super Enkripsi (Extended Vigenere + transposisi kolom)
8. Enigma (bonus 1)

Bonus 2 (bahasa Ruby) ada di proyek terpisah, folder `kripto_ruby`, dengan README sendiri.

## Cara menjalankan
1. Pastikan Python 3 sudah terpasang.
2. Buka terminal di folder proyek ini, lalu pasang library yang dibutuhkan:

        pip install -r requirements.txt

3. Jalankan program:

        python app.py

4. Buka browser dan masuk ke alamat http://127.0.0.1:5000

## Cara memakai
1. Pilih cipher di daftar sebelah kiri.
2. Pilih jenis input: **Teks** (ketik pesan) atau **File** (pilih file apa saja).
3. Isi **Kunci**. Contoh format kunci ada di bawah tombol atau di tabel berikut.
4. Klik **Enkripsi** untuk mengacak pesan, atau **Dekripsi** untuk mengembalikannya.
5. Hasil tampil dalam kode base64. Klik **Unduh sebagai file biner** untuk menyimpan hasilnya.

Untuk mendekripsi teks, tempel hasil base64 ke kotak teks lalu klik **Dekripsi** dengan kunci yang sama.
Untuk mendekripsi file, pilih file `.dat` hasil enkripsi lalu klik **Dekripsi**.

## Format kunci
| Cipher | Isi kunci | Contoh |
|---|---|---|
| Vigenere, Auto-Key, Playfair | Satu kata, hanya huruf | `SECRET` |
| Extended Vigenere | Teks bebas | `rahasia` |
| Affine | Dua angka `a,b`; a harus koprima dengan 26 | `5,8` |
| Hill | Angka-angka matriks n x n; determinannya harus koprima dengan 26 | `3 3 2 5` (matriks 2x2) |
| Enigma | 3 huruf posisi awal rotor, boleh ditambah pasangan plugboard | `ABC` atau `ABC AB CD` |
| Super Enkripsi | Teks bebas; panjang kunci menentukan jumlah kolom transposisi | `rahasia` |

## Hal yang perlu diketahui
- **File yang dienkripsi** disimpan sebagai `cipherteks.dat`. Di dalamnya sudah tersimpan nama dan ekstensi file asli, jadi saat didekripsi file kembali dengan nama aslinya (misalnya `cat.jpeg`).
- **Cipher 26 huruf** (Vigenere, Auto-Key, Playfair, Affine, Hill, Enigma) hanya memproses huruf A-Z. Angka, spasi, dan tanda baca dibuang. Karena itu cipher ini cocok untuk teks, bukan untuk file seperti gambar atau docx. Untuk file, gunakan **Extended Vigenere** atau **Super Enkripsi**.
- **Playfair dan Hill**: huruf `X` bisa ditambahkan sebagai pengisi, dan di Playfair huruf J digabung dengan I. Huruf tambahan itu tetap muncul di hasil dekripsi.
- **Enigma**: enkripsi dan dekripsi memakai langkah yang sama, asalkan kuncinya sama.
- Kunci Extended Vigenere dan Super Enkripsi membedakan huruf besar dan kecil (`rahasia` berbeda dengan `RAHASIA`). Untuk cipher 26 huruf, besar atau kecil tidak berpengaruh.

## Struktur folder
    app.py              program utama (server dan semua cipher)
    requirements.txt    daftar library
    templates/          halaman web (index.html)
    static/             tampilan (style.css) dan skrip (app.js)