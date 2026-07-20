# Star Falling — GSAP ScrollTrigger Video Scrub
### Dokumentasi Implementasi untuk Webflow 3Koncept

**Versi:** 1.0 · **Target section:** `.section-star-falling`

---

## 1. Ringkasan: kenapa bukan `<video>`?

Yang Anda lihat di oryzo.ai **bukan** video yang di-scrub. Itu **canvas image sequence**.

Alasannya teknis: `video.currentTime = x` memaksa browser melakukan *seek* ke keyframe terdekat lalu men-decode maju sampai frame target. Di Chrome desktop ini kadang mulus; di **Safari dan iOS praktis selalu tersendat**, karena seek bersifat asynchronous dan di-throttle. Tidak ada cara mengakalinya secara andal.

Solusi industri (Apple AirPods page, oryzo.ai, Locomotive) adalah: pecah video jadi frame gambar, preload semuanya, lalu gambar frame ke `<canvas>` sesuai posisi scroll. Menggambar gambar yang sudah ada di memori itu **instan** — tidak ada decode, tidak ada seek. Hasilnya mulus 100% di semua browser.

**Yang sudah saya siapkan dari video Anda:**

| Spesifikasi | Nilai |
|---|---|
| Video asli | 2880×2182 · 60fps · 5,02 detik · 4,5 MB |
| Frame sequence | 151 frame @ 30fps (cukup untuk scrub — mata tidak bisa membedakan) |
| Format | WebP (≈50% lebih ringan dari JPEG pada kualitas setara) |
| **Total payload** | **1,7 MB** (sprite sheet) — *lebih ringan dari video aslinya* |

---

## 2. Dua opsi hosting — pilih salah satu

Ini satu-satunya keputusan penting yang perlu Anda ambil.

### ✅ Opsi A — Sprite Sheet (REKOMENDASI untuk Webflow)

151 frame dikemas jadi **7 file gambar besar**, masing-masing berisi grid 5×5 frame. Canvas mengambil potongan yang tepat dengan `drawImage()`.

- **Upload:** 7 file ke Webflow Assets. Selesai.
- **Total:** 1,7 MB
- **Kelebihan:** murni Webflow, tidak butuh layanan eksternal, hanya 7 HTTP request
- **Kekurangan:** resolusi per frame 960×728 — sangat baik untuk section, sedikit lebih lembut dari Opsi B di monitor 4K

📁 File ada di `starfall/sprites/` — sudah siap upload.

### Opsi B — Frame Individual + CDN eksternal

151 file terpisah, resolusi penuh 1440px atau 1920px.

- **Upload:** ke GitHub → disajikan gratis lewat jsDelivr
- **Total:** 3,0 MB (1440px) atau 4,2 MB (1920px)
- **Kelebihan:** kualitas maksimal
- **Kekurangan:** butuh akun GitHub; 151 request (walau HTTP/2 menanganinya dengan baik)

> ⚠️ **Jangan upload 151 frame individual ke Webflow Assets.** Webflow memberi setiap aset URL dengan hash acak (`.../65f2a1_frame_0001.webp`), sehingga Anda tidak bisa membuat pola URL `frame_{i}.webp`. Anda harus menyalin 151 URL satu per satu. Ini alasan utama Opsi A ada.

📁 File ada di `starfall/downloads/` (3 varian resolusi, sudah di-zip).

**Saran saya: mulai dengan Opsi A.** Jika nanti terlihat kurang tajam di layar besar, baru pindah ke Opsi B — kodenya sama, cukup ganti satu baris config.

---

## 3. Struktur Webflow

Bangun struktur ini di dalam section yang sudah Anda punya:

```
Section  .section-star-falling
│    position: relative
│    height:   100vh
│    overflow: hidden
│    background-color: #000000
│
└── HTML Embed  (isi: starfall-embed.html)
     └── <canvas id="starfall-canvas">
```

**Itu saja.** Tidak perlu `position: sticky` dan tidak perlu section setinggi 300vh — ScrollTrigger yang menangani pinning dan otomatis menyisipkan spacer scroll-nya sendiri (`pinSpacing: true`).

### Pengaturan style di Designer

Pilih `.section-star-falling`, lalu set:

| Properti | Nilai | Kenapa |
|---|---|---|
| Position | `Relative` | Jangkar untuk canvas yang `absolute` |
| Height | `100vh` | Section mengisi satu layar penuh saat di-pin |
| Overflow | `Hidden` | Mencegah canvas bocor saat cover-fit meng-crop |
| Background | `#000000` | Menghindari kedip putih sebelum frame pertama tampil |

---

## 4. Langkah implementasi

### Langkah 1 — Muat GSAP

**Site Settings → Custom Code → Head Code** (berlaku untuk seluruh site — lebih baik daripada per halaman karena browser bisa cache-nya):

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/gsap.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/gsap@3.12.5/dist/ScrollTrigger.min.js"></script>
```

> Webflow memang memakai GSAP secara internal untuk Interactions, tapi versi itu di-bundle dan **tidak** terekspos sebagai `window.gsap`. Anda tetap harus memuatnya sendiri.

### Langkah 2 — Upload sprite sheet

1. Webflow → **Assets** panel → drag ke-7 file dari `starfall/sprites/`
2. Klik tiap aset → **Copy URL** (ikon link)
3. Simpan ke-7 URL secara berurutan (sheet_1 → sheet_7). **Urutan sangat penting.**

URL-nya akan seperti:
```
https://cdn.prod.website-files.com/{site-id}/{hash}_starfall_sheet_1.webp
```

### Langkah 3 — Pasang Embed

1. Drag komponen **HTML Embed** ke dalam `.section-star-falling`
2. Buka `starfall/embed/starfall-embed.html`, salin **seluruh isinya**
3. Tempel ke Embed
4. Ganti ketujuh `PASTE_URL_SHEET_n` dengan URL dari Langkah 2

```js
sheets: [
  'https://cdn.prod.website-files.com/abc123/def456_starfall_sheet_1.webp',
  'https://cdn.prod.website-files.com/abc123/def789_starfall_sheet_2.webp',
  // … dan seterusnya sampai sheet 7
],
```

### Langkah 4 — Publish & uji

Custom code **tidak jalan di Designer Preview**. Anda harus Publish ke staging (`3koncept.webflow.io`) untuk mengujinya.

---

## 5. Panduan konfigurasi

Semua yang bisa diatur ada di blok `CONFIG` di bagian atas script:

| Parameter | Default | Fungsi |
|---|---|---|
| `mode` | `'sprite'` | `'sprite'` (Opsi A) atau `'sequence'` (Opsi B) |
| `scrollLength` | `'+=300%'` | Jarak scroll selama section di-pin. `300%` = 3× tinggi viewport. **Naikkan** agar animasi terasa lebih lambat/panjang, **turunkan** agar lebih cepat. |
| `scrub` | `0.6` | `true`/`0` = terkunci persis ke scroll (agak kaku). `0.6` memberi jeda 0,6 detik sehingga terasa punya bobot. Coba `0.3`–`1.2`. |
| `frameCount` | `151` | Jumlah frame. Jangan diubah kecuali Anda men-generate ulang aset. |
| `pinSpacing` | `true` | `true` = section berikutnya terdorong ke bawah (normal). `false` = section berikutnya menimpa (efek overlap). |
| `maxDPR` | `2` | Batas device pixel ratio. Turunkan ke `1.5` jika ada masalah performa di retina. |
| `debug` | `false` | `true` menampilkan marker start/end ScrollTrigger. Sangat membantu saat setup. |

### Beralih ke Opsi B (frame individual)

```js
mode: 'sequence',
sequenceUrl: 'https://cdn.jsdelivr.net/gh/USERNAME/REPO@main/frames/frame_{i}.webp',
pad: 4,
```

`{i}` otomatis diganti jadi `0001`, `0002`, … Cara menyiapkan repo-nya:

```bash
# ekstrak starfall-frames-1440.zip, lalu:
git init && git add . && git commit -m "starfall frames"
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```
jsDelivr langsung menyajikannya — tanpa registrasi.

---

## 6. Preview lokal

Sebelum menyentuh Webflow, buka:

```
starfall/preview/starfall-preview.html
```

Halaman ini berjalan langsung dari komputer Anda dengan sprite sheet lokal, lengkap dengan HUD di pojok kiri atas yang menampilkan nomor frame aktif. Gunakan untuk menentukan nilai `scrollLength` dan `scrub` yang pas sebelum memindahkannya ke Webflow.

---

## 7. Cara kerja kodenya

Empat bagian yang perlu Anda pahami kalau nanti mau memodifikasi:

**Preload.** Ke-7 sheet dimuat via `Promise.all`. Sheet pertama dimuat lebih dulu dan langsung digambar, sehingga frame pertama muncul cepat sementara sisanya menyusul. Kalau user scroll ke frame yang sheet-nya belum siap, `render()` keluar lebih awal dan frame terakhir tetap terpampang — tidak pernah ada layar kosong.

**Cover-fit.** Canvas tidak punya `object-fit`, jadi harus dihitung manual:
```js
var scale = Math.max(cw / sourceW, ch / sourceH);
```
`Math.max` = cover (isi penuh, crop kelebihannya). Kalau Anda mau `contain` (seluruh frame terlihat, ada letterbox), ganti jadi `Math.min`.

**Frame mapping.** Frame ke-`f` ada di sheet `Math.floor(f / 25)`, pada posisi grid `f % 25`. Dari situ `drawImage()` dipanggil dengan 9 argumen — 4 pertama memotong sumber, 4 terakhir menentukan tujuan.

**Scrub.** GSAP men-*tween* properti `state.frame` dari 0 ke 150 dengan `ease: 'none'`, terikat ke ScrollTrigger. Setiap update memanggil `render()`. Ini lebih baik daripada membaca `scrollY` manual karena ScrollTrigger sudah menangani smoothing, throttling, dan sinkronisasi dengan refresh rate layar.

---

## 8. Troubleshooting

| Gejala | Penyebab | Solusi |
|---|---|---|
| Canvas hitam total | URL sheet salah / masih placeholder | Buka DevTools Console — script mencetak `[starfall] failed to load <url>` |
| Console: *"GSAP or ScrollTrigger is missing"* | Script CDN belum dimuat | Cek Site Settings → Custom Code → Head |
| Tidak ada yang terjadi saat scroll | Section tidak ketemu | Pastikan class-nya persis `section-star-falling` |
| Animasi mulai terlalu awal/telat | Titik trigger meleset | Set `debug: true` untuk melihat marker, lalu sesuaikan `start` |
| Gambar gepeng / peyot | Section belum `overflow: hidden` | Set di Designer |
| Tersendat di mobile | DPR terlalu tinggi | Turunkan `maxDPR` ke `1.5` |
| Posisi pin kacau setelah font/gambar lain load | ScrollTrigger menghitung tinggi terlalu awal | Sudah ditangani `ScrollTrigger.refresh()` pasca-preload; kalau masih terjadi, panggil `ScrollTrigger.refresh()` lagi di `window.load` |
| Jalan di Preview tapi tidak di live | Custom code memang tidak jalan di Designer | Publish dulu |

---

## 9. Scalability & maintenance

**Untuk mengganti videonya nanti:** yang perlu di-regenerate hanya asetnya — kodenya tidak berubah kecuali `frameCount`.

```bash
# 1. ekstrak frame @30fps, lebar 1440, WebP
ffmpeg -i source.mp4 -vf "fps=30,scale=1440:-2" \
  -c:v libwebp -quality 72 -compression_level 6 frames/frame_%04d.webp

# 2. kemas jadi sprite sheet — lihat starfall/tools/build-sprites.py
python3 build-sprites.py
```

**Kalau nanti ada beberapa section scrub di site ini:** ubah script jadi mengambil config dari atribut `data-*` pada section, lalu jalankan `querySelectorAll('[data-starfall]')` dalam loop. Dengan begitu satu script di Site-wide Footer bisa melayani berapa pun section, dan Designer tetap jadi sumber kebenaran untuk parameternya. Beri tahu saya kalau sudah sampai tahap itu — saya siapkan versinya.

**Kalau nanti masuk CMS:** simpan URL sheet di field CMS `Sheet 1 URL` … `Sheet 7 URL` pada collection, lalu di embed pakai `{{wf {"path":"sheet-1-url"} }}`. Tapi untuk satu hero section, hard-code jauh lebih sederhana dan lebih cepat.

---

## 10. Isi folder

```
starfall/
├── README-starfall.md              ← dokumen ini
├── embed/
│   └── starfall-embed.html         ← salin ini ke Webflow HTML Embed
├── sprites/                        ← UPLOAD KE WEBFLOW ASSETS (7 file, 1,7 MB)
│   ├── starfall_sheet_1..7.webp
│   └── manifest.json               ← spesifikasi grid (referensi)
├── preview/
│   └── starfall-preview.html       ← uji lokal sebelum ke Webflow
├── tools/
│   └── build-sprites.py            ← regenerate sheet dari frame baru
└── downloads/
    ├── starfall-frames-1440.zip    ← Opsi B, 151 frame, 3,0 MB
    ├── starfall-frames-1920.zip    ← Opsi B kualitas tinggi, 4,2 MB
    └── starfall-frames-800-mobile.zip ← 120 frame @24fps, 1,0 MB
```
