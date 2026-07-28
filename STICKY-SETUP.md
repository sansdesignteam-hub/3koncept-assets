# Starfall — Sticky via Webflow (bukan GSAP pin)

Panduan struktur untuk membuat canvas setinggi band tertentu (bukan full-screen)
dan sticky-nya ditangani CSS Webflow, bukan `pin` milik ScrollTrigger.

---

## Struktur

```
Section  .section-star-falling          ← tinggi PANJANG, ini yang bikin scroll
│   position: relative
│   height:   400vh          ← durasi animasi. Panjangin = lebih lambat
│   overflow: VISIBLE        ← ⚠ WAJIB. hidden/auto membunuh sticky
│
└── Div  .starfall-sticky               ← yang menempel di layar
    │   position: sticky
    │   top:      0
    │   height:   100vh
    │   overflow: VISIBLE
    │
    └── Div  .starfall-stage            ← KOTAK MERAH di screenshot Anda
        │   position: relative
        │   width:    100%
        │   height:   52vh   ← atur bebas di Designer
        │   overflow: hidden
        │
        └── HTML Embed  → <canvas id="starfall-canvas">
```

Yang mengatur tinggi video sekarang adalah **`.starfall-stage`**. Canvas selalu
mengisi penuh induknya, jadi Anda cukup menggeser angka `height` di Designer —
tidak perlu menyentuh kode sama sekali.

Dari screenshot Anda, kotak merah ≈ 51% tinggi viewport. Mulai dari `52vh`.

---

## Kenapa tiga div, bukan satu?

Tiap lapis punya satu tugas dan tidak bisa digabung:

- **`.section-star-falling`** menyediakan jarak scroll. Sticky butuh induk yang
  lebih tinggi dari dirinya — kalau tingginya sama, tidak ada ruang untuk menempel.
- **`.starfall-sticky`** yang benar-benar menempel. Tingginya `100vh` supaya
  melepas tepat saat section habis.
- **`.starfall-stage`** membatasi tinggi tampilan video. Dipisah dari
  `.starfall-sticky` karena `overflow: hidden` yang dibutuhkan untuk crop
  **tidak boleh** dipasang di elemen sticky atau induknya.

---

## Perubahan config

Sudah saya set di `embed/starfall-embed.html`:

```js
usePin: false,      // GSAP tidak lagi nge-pin; CSS sticky yang kerja
fit:    'contain',  // frame utuh, tidak ke-crop
alignX: 0.5,
alignY: 0.5,
```

**Kenapa `contain`, bukan `cover`?** Frame sumbernya 1440×1092 (rasio 1,32 —
hampir kotak). Stage Anda sekarang lebar dan pendek (rasio ±3,4). Dengan `cover`,
canvas akan memperbesar frame sampai memenuhi lebar lalu memotong atas-bawah
habis-habisan — bintang jatuhnya kemungkinan besar ter-crop keluar layar.
`contain` menampilkan frame utuh. Karena framenya transparan, tidak ada bar hitam
letterbox seperti pada video biasa — yang tersisa hanya area kosong yang tembus
ke background section.

Konsekuensinya bintangnya jadi lebih kecil (dibatasi tinggi stage). Kalau kurang
besar, ada dua jalan: naikkan `height` di `.starfall-stage`, atau ganti ke
`fit: 'cover'` lalu atur `alignY` untuk memilih bagian mana yang dipertahankan
(`0` = tahan bagian atas, `1` = bagian bawah).

Dengan `usePin: false`, `scrollLength` **tidak lagi berpengaruh**. Durasi animasi
kini murni ditentukan `height` pada `.section-star-falling`:

| Height section | Efek |
|---|---|
| `200vh` | cepat, agresif |
| `400vh` | seimbang — mulai dari sini |
| `600vh` | lambat, sinematik |

---

## Jebakan `overflow`

`position: sticky` gagal tanpa suara kalau **ada satu saja** leluhur yang punya
`overflow` selain `visible` — termasuk `hidden`, `auto`, atau `scroll`. Tidak ada
error, elemennya cuma diam saja seolah `position: static`.

Ini penting untuk Anda: dokumentasi awal menyuruh memasang `overflow: hidden` di
`.section-star-falling`. **Itu harus dicabut sekarang** — pindahkan ke
`.starfall-stage`.

Saya sudah menanam pengecekan di script. Kalau ada leluhur bermasalah, Console
akan menampilkan:

```
[starfall] Ancestor <div.page-wrapper> has overflow:hidden — this breaks position:sticky.
```

Periksa juga `body` dan `.page-wrapper` — dua tempat paling sering.

---

## Checklist

1. Bungkus canvas dengan `.starfall-sticky` → `.starfall-stage`
2. `.section-star-falling`: height `400vh`, overflow **Visible**
3. `.starfall-sticky`: position Sticky, top `0`, height `100vh`
4. `.starfall-stage`: height `52vh`, overflow Hidden
5. Tempel ulang `starfall-embed.html` ke HTML Embed
6. Publish, cek Console — pastikan tidak ada peringatan overflow
7. Setel `height` `.starfall-stage` dan `.section-star-falling` sesuai selera

Untuk kembali ke perilaku lama (GSAP yang nge-pin, full-screen), set
`usePin: true` dan `fit: 'cover'` — struktur div-nya tidak perlu diubah.
