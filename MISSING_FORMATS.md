# Missing Format Combinations Analysis

Comprehensive analysis of untested format combinations based on ffprobe capabilities.

---

## Summary Statistics

| Category | Total Available | Currently Tested | Missing |
|----------|-----------------|------------------|---------|
| **Container Formats** | 181 | 4 | 177 |
| **Video Codecs** | 99 | 10 | 89 |
| **Audio Codecs** | 76 | 6 | 70 |
| **Pixel Formats** | 200 | 0 | 200 |

## Missing Container Formats

Container formats that can be encoded but have not been tested:

| Format | Description | Status |
|--------|-------------|--------|
| `3g2` | 3GP2 (3GPP2 file format) | ❌ Not tested |
| `3gp` | 3GP (3GPP file format) | ❌ Not tested |
| `a64` | a64 - video for Commodore 64 | ❌ Not tested |
| `ac3` | raw AC-3 | ❌ Not tested |
| `ac4` | raw AC-4 | ❌ Not tested |
| `adts` | ADTS AAC (Advanced Audio Coding) | ❌ Not tested |
| `adx` | CRI ADX | ❌ Not tested |
| `aea` | MD STUDIO audio | ❌ Not tested |
| `aiff` | Audio IFF | ❌ Not tested |
| `alaw` | PCM A-law | ❌ Not tested |
| `alp` | LEGO Racers ALP | ❌ Not tested |
| `amr` | 3GPP AMR | ❌ Not tested |
| `amv` | AMV | ❌ Not tested |
| `apm` | Ubisoft Rayman 2 APM | ❌ Not tested |
| `apng` | Animated Portable Network Graphics | ❌ Not tested |
| `aptx` | raw aptX (Audio Processing Technology for Bluetooth) | ❌ Not tested |
| `aptx_hd` | raw aptX HD (Audio Processing Technology for Bluetooth) | ❌ Not tested |
| `apv` | APV raw bitstream | ❌ Not tested |
| `argo_asf` | Argonaut Games ASF | ❌ Not tested |
| `argo_cvg` | Argonaut Games CVG | ❌ Not tested |
| `asf` | ASF (Advanced / Active Streaming Format) | ❌ Not tested |
| `asf_stream` | ASF (Advanced / Active Streaming Format) | ❌ Not tested |
| `ass` | SSA (SubStation Alpha) subtitle | ❌ Not tested |
| `ast` | AST (Audio Stream) | ❌ Not tested |
| `au` | Sun AU | ❌ Not tested |
| `avi` | AVI (Audio Video Interleaved) | ❌ Not tested |
| `avif` | AVIF | ❌ Not tested |
| `avm2` | SWF (ShockWave Flash) (AVM2) | ❌ Not tested |
| `avs2` | raw AVS2-P2/IEEE1857.4 video | ❌ Not tested |
| `avs3` | AVS3-P2/IEEE1857.10 | ❌ Not tested |
| `bit` | G.729 BIT file format | ❌ Not tested |
| `caf` | Apple CAF (Core Audio Format) | ❌ Not tested |
| `cavsvideo` | raw Chinese AVS (Audio Video Standard) video | ❌ Not tested |
| `codec2` | codec2 .c2 muxer | ❌ Not tested |
| `codec2raw` | raw codec2 muxer | ❌ Not tested |
| `crc` | CRC testing | ❌ Not tested |
| `dash` | DASH Muxer | ❌ Not tested |
| `data` | raw data | ❌ Not tested |
| `daud` | D-Cinema audio | ❌ Not tested |
| `dfpwm` | raw DFPWM1a | ❌ Not tested |
| `dirac` | raw Dirac | ❌ Not tested |
| `dnxhd` | raw DNxHD (SMPTE VC-3) | ❌ Not tested |
| `dts` | raw DTS | ❌ Not tested |
| `dv` | DV (Digital Video) | ❌ Not tested |
| `dvd` | MPEG-2 PS (DVD VOB) | ❌ Not tested |
| `eac3` | raw E-AC-3 | ❌ Not tested |
| `evc` | raw EVC video | ❌ Not tested |
| `f32be` | PCM 32-bit floating-point big-endian | ❌ Not tested |
| `f32le` | PCM 32-bit floating-point little-endian | ❌ Not tested |
| `f4v` | F4V Adobe Flash Video | ❌ Not tested |
| `f64be` | PCM 64-bit floating-point big-endian | ❌ Not tested |
| `f64le` | PCM 64-bit floating-point little-endian | ❌ Not tested |
| `ffmetadata` | FFmpeg metadata in text | ❌ Not tested |
| `fifo` | FIFO queue pseudo-muxer | ❌ Not tested |
| `film_cpk` | Sega FILM / CPK | ❌ Not tested |
| `filmstrip` | Adobe Filmstrip | ❌ Not tested |
| `fits` | Flexible Image Transport System | ❌ Not tested |
| `flac` | raw FLAC | ❌ Not tested |
| `flv` | FLV (Flash Video) | ❌ Not tested |
| `framecrc` | framecrc testing | ❌ Not tested |
| `framehash` | Per-frame hash testing | ❌ Not tested |
| `framemd5` | Per-frame MD5 testing | ❌ Not tested |
| `g722` | raw G.722 | ❌ Not tested |
| `g723_1` | raw G.723.1 | ❌ Not tested |
| `g726` | raw big-endian G.726 ("left-justified") | ❌ Not tested |
| `g726le` | raw little-endian G.726 ("right-justified") | ❌ Not tested |
| `gif` | CompuServe Graphics Interchange Format (GIF) | ❌ Not tested |
| `gsm` | raw GSM | ❌ Not tested |
| `gxf` | GXF (General eXchange Format) | ❌ Not tested |
| `h261` | raw H.261 | ❌ Not tested |
| `h263` | raw H.263 | ❌ Not tested |
| `h264` | raw H.264 video | ❌ Not tested |
| `hash` | Hash testing | ❌ Not tested |
| `hds` | HDS Muxer | ❌ Not tested |
| `hevc` | raw HEVC video | ❌ Not tested |
| `hls` | Apple HTTP Live Streaming | ❌ Not tested |
| `iamf` | Raw Immersive Audio Model and Formats | ❌ Not tested |
| `ico` | Microsoft Windows ICO | ❌ Not tested |
| `ilbc` | iLBC storage | ❌ Not tested |
| `image2` | image2 sequence | ❌ Not tested |
| `image2pipe` | piped image2 sequence | ❌ Not tested |
| `ipod` | iPod H.264 MP4 (MPEG-4 Part 14) | ❌ Not tested |
| `ircam` | Berkeley/IRCAM/CARL Sound Format | ❌ Not tested |
| `ismv` | ISMV/ISMA (Smooth Streaming) | ❌ Not tested |
| `ivf` | On2 IVF | ❌ Not tested |
| `jacosub` | JACOsub subtitle format | ❌ Not tested |
| `kvag` | Simon & Schuster Interactive VAG | ❌ Not tested |
| `latm` | LOAS/LATM | ❌ Not tested |
| `lc3` | LC3 (Low Complexity Communication Codec) | ❌ Not tested |
| `lrc` | LRC lyrics | ❌ Not tested |
| `m4v` | raw MPEG-4 video | ❌ Not tested |
| `matroska` | Matroska | ❌ Not tested |
| `mcc` | MacCaption | ❌ Not tested |
| `md5` | MD5 testing | ❌ Not tested |
| `microdvd` | MicroDVD subtitle format | ❌ Not tested |
| `mjpeg` | raw MJPEG video | ❌ Not tested |
| `mkvtimestamp_v2` | extract pts as timecode v2 format, as defined by mkvtoolnix | ❌ Not tested |
| `mlp` | raw MLP | ❌ Not tested |
| `mmf` | Yamaha SMAF | ❌ Not tested |
| `mp2` | MP2 (MPEG audio layer 2) | ❌ Not tested |
| `mp3` | MP3 (MPEG audio layer 3) | ❌ Not tested |
| `mp4` | MP4 (MPEG-4 Part 14) | ❌ Not tested |
| `mpeg` | MPEG-1 Systems / MPEG program stream | ❌ Not tested |
| `mpeg1video` | raw MPEG-1 video | ❌ Not tested |
| `mpeg2video` | raw MPEG-2 video | ❌ Not tested |
| `mpegts` | MPEG-TS (MPEG-2 Transport Stream) | ❌ Not tested |
| `mpjpeg` | MIME multipart JPEG | ❌ Not tested |
| `mulaw` | PCM mu-law | ❌ Not tested |
| `mxf` | MXF (Material eXchange Format) | ❌ Not tested |
| `mxf_d10` | MXF (Material eXchange Format) D-10 Mapping | ❌ Not tested |
| `mxf_opatom` | MXF (Material eXchange Format) Operational Pattern Atom | ❌ Not tested |
| `null` | raw null video | ❌ Not tested |
| `nut` | NUT | ❌ Not tested |
| `obu` | AV1 low overhead OBU | ❌ Not tested |
| `oga` | Ogg Audio | ❌ Not tested |
| `ogg` | Ogg | ❌ Not tested |
| `oma` | Sony OpenMG audio | ❌ Not tested |
| `opus` | Ogg Opus | ❌ Not tested |
| `psp` | PSP MP4 (MPEG-4 Part 14) | ❌ Not tested |
| `rawvideo` | raw video | ❌ Not tested |
| `rcwt` | RCWT (Raw Captions With Time) | ❌ Not tested |
| `rm` | RealMedia | ❌ Not tested |
| `roq` | raw id RoQ | ❌ Not tested |
| `rso` | Lego Mindstorms RSO | ❌ Not tested |
| `rtp` | RTP output | ❌ Not tested |
| `rtp_mpegts` | RTP/mpegts output format | ❌ Not tested |
| `rtsp` | RTSP output | ❌ Not tested |
| `s16be` | PCM signed 16-bit big-endian | ❌ Not tested |
| `s16le` | PCM signed 16-bit little-endian | ❌ Not tested |
| `s24be` | PCM signed 24-bit big-endian | ❌ Not tested |
| `s24le` | PCM signed 24-bit little-endian | ❌ Not tested |
| `s32be` | PCM signed 32-bit big-endian | ❌ Not tested |
| `s32le` | PCM signed 32-bit little-endian | ❌ Not tested |
| `s8` | PCM signed 8-bit | ❌ Not tested |
| `sap` | SAP output | ❌ Not tested |
| `sbc` | raw SBC | ❌ Not tested |
| `scc` | Scenarist Closed Captions | ❌ Not tested |
| `segment` | segment | ❌ Not tested |
| `smjpeg` | Loki SDL MJPEG | ❌ Not tested |
| `smoothstreaming` | Smooth Streaming Muxer | ❌ Not tested |
| `sox` | SoX (Sound eXchange) native | ❌ Not tested |
| `spdif` | IEC 61937 (used on S/PDIF - IEC958) | ❌ Not tested |
| `spx` | Ogg Speex | ❌ Not tested |
| `srt` | SubRip subtitle | ❌ Not tested |
| `stream_segment,ssegment` | streaming segment muxer | ❌ Not tested |
| `streamhash` | Per-stream hash testing | ❌ Not tested |
| `sup` | raw HDMV Presentation Graphic Stream subtitles | ❌ Not tested |
| `svcd` | MPEG-2 PS (SVCD) | ❌ Not tested |
| `swf` | SWF (ShockWave Flash) | ❌ Not tested |
| `tee` | Multiple muxer tee | ❌ Not tested |
| `truehd` | raw TrueHD | ❌ Not tested |
| `tta` | TTA (True Audio) | ❌ Not tested |
| `ttml` | TTML subtitle | ❌ Not tested |
| `u16be` | PCM unsigned 16-bit big-endian | ❌ Not tested |
| `u16le` | PCM unsigned 16-bit little-endian | ❌ Not tested |
| `u24be` | PCM unsigned 24-bit big-endian | ❌ Not tested |
| `u24le` | PCM unsigned 24-bit little-endian | ❌ Not tested |
| `u32be` | PCM unsigned 32-bit big-endian | ❌ Not tested |
| `u32le` | PCM unsigned 32-bit little-endian | ❌ Not tested |
| `u8` | PCM unsigned 8-bit | ❌ Not tested |
| `uncodedframecrc` | uncoded framecrc testing | ❌ Not tested |
| `vc1` | raw VC-1 video | ❌ Not tested |
| `vc1test` | VC-1 test bitstream | ❌ Not tested |
| `vcd` | MPEG-1 Systems / MPEG program stream (VCD) | ❌ Not tested |
| `vidc` | PCM Archimedes VIDC | ❌ Not tested |
| `vob` | MPEG-2 PS (VOB) | ❌ Not tested |
| `voc` | Creative Voice | ❌ Not tested |
| `vvc` | raw H.266/VVC video | ❌ Not tested |
| `w64` | Sony Wave64 | ❌ Not tested |
| `wav` | WAV / WAVE (Waveform Audio) | ❌ Not tested |
| `webm_chunk` | WebM Chunk Muxer | ❌ Not tested |
| `webm_dash_manifest` | WebM DASH Manifest | ❌ Not tested |
| `webp` | WebP | ❌ Not tested |
| `webvtt` | WebVTT subtitle | ❌ Not tested |
| `wsaud` | Westwood Studios audio | ❌ Not tested |
| `wtv` | Windows Television (WTV) | ❌ Not tested |
| `wv` | raw WavPack | ❌ Not tested |
| `yuv4mpegpipe` | YUV4MPEG pipe | ❌ Not tested |

**Total missing containers**: 178

## Missing Video Codecs

Video codecs that can be encoded but have not been tested:

| Codec | Description | Status |
|-------|-------------|--------|
| `a64_multi` | Multicolor charset for Commodore 64 (encoders: a64multi) | ❌ Not tested |
| `a64_multi5` | Multicolor charset for Commodore 64, extended with 5th color (colram) (encoders: a64multi5) | ❌ Not tested |
| `alias_pix` | Alias/Wavefront PIX image | ❌ Not tested |
| `amv` | AMV Video | ❌ Not tested |
| `apng` | APNG (Animated Portable Network Graphics) image | ❌ Not tested |
| `asv1` | ASUS V1 | ❌ Not tested |
| `asv2` | ASUS V2 | ❌ Not tested |
| `avrp` | Avid 1:1 10-bit RGB Packer | ❌ Not tested |
| `avui` | Avid Meridien Uncompressed | ❌ Not tested |
| `bitpacked` | Bitpacked | ❌ Not tested |
| `bmp` | BMP (Windows and OS/2 bitmap) | ❌ Not tested |
| `cfhd` | GoPro CineForm HD | ❌ Not tested |
| `cinepak` | Cinepak | ❌ Not tested |
| `cljr` | Cirrus Logic AccuPak | ❌ Not tested |
| `dirac` | Dirac (encoders: vc2) | ❌ Not tested |
| `dpx` | DPX (Digital Picture Exchange) image | ❌ Not tested |
| `dvvideo` | DV (Digital Video) | ❌ Not tested |
| `dxv` | Resolume DXV | ❌ Not tested |
| `exr` | OpenEXR image | ❌ Not tested |
| `ffv1` | FFmpeg video codec #1 | ❌ Not tested |
| `ffvhuff` | Huffyuv FFmpeg variant | ❌ Not tested |
| `fits` | FITS (Flexible Image Transport System) | ❌ Not tested |
| `flashsv` | Flash Screen Video v1 | ❌ Not tested |
| `flashsv2` | Flash Screen Video v2 | ❌ Not tested |
| `flv1` | FLV / Sorenson Spark / Sorenson H.263 (Flash Video) (decoders: flv) (encoders: flv) | ❌ Not tested |
| `gif` | CompuServe GIF (Graphics Interchange Format) | ❌ Not tested |
| `h261` | H.261 | ❌ Not tested |
| `h263` | H.263 / H.263-1996, H.263+ / H.263-1998 / H.263 version 2 | ❌ Not tested |
| `h263p` | H.263+ / H.263-1998 / H.263 version 2 | ❌ Not tested |
| `hap` | Vidvox Hap | ❌ Not tested |
| `hdr` | HDR (Radiance RGBE format) image | ❌ Not tested |
| `huffyuv` | HuffYUV | ❌ Not tested |
| `jpeg2000` | JPEG 2000 (encoders: jpeg2000 libopenjpeg) | ❌ Not tested |
| `jpegls` | JPEG-LS | ❌ Not tested |
| `jpegxl` | JPEG XL (decoders: libjxl) (encoders: libjxl) | ❌ Not tested |
| `jpegxl_anim` | JPEG XL animated (decoders: libjxl_anim) (encoders: libjxl_anim) | ❌ Not tested |
| `ljpeg` | Lossless JPEG | ❌ Not tested |
| `magicyuv` | MagicYUV video | ❌ Not tested |
| `mjpeg` | Motion JPEG | ❌ Not tested |
| `mpeg1video` | MPEG-1 video | ❌ Not tested |
| `mpeg2video` | MPEG-2 video (decoders: mpeg2video mpegvideo) | ❌ Not tested |
| `mpeg4` | MPEG-4 part 2 (encoders: mpeg4 libxvid) | ❌ Not tested |
| `msmpeg4v2` | MPEG-4 part 2 Microsoft variant version 2 | ❌ Not tested |
| `msmpeg4v3` | MPEG-4 part 2 Microsoft variant version 3 (decoders: msmpeg4) (encoders: msmpeg4) | ❌ Not tested |
| `msrle` | Microsoft RLE | ❌ Not tested |
| `msvideo1` | Microsoft Video 1 | ❌ Not tested |
| `pam` | PAM (Portable AnyMap) image | ❌ Not tested |
| `pbm` | PBM (Portable BitMap) image | ❌ Not tested |
| `pcx` | PC Paintbrush PCX image | ❌ Not tested |
| `pfm` | PFM (Portable FloatMap) image | ❌ Not tested |
| `pgm` | PGM (Portable GrayMap) image | ❌ Not tested |
| `pgmyuv` | PGMYUV (Portable GrayMap YUV) image | ❌ Not tested |
| `phm` | PHM (Portable HalfFloatMap) image | ❌ Not tested |
| `png` | PNG (Portable Network Graphics) image | ❌ Not tested |
| `ppm` | PPM (Portable PixelMap) image | ❌ Not tested |
| `qoi` | QOI (Quite OK Image) | ❌ Not tested |
| `qtrle` | QuickTime Animation (RLE) video | ❌ Not tested |
| `r10k` | AJA Kona 10-bit RGB Codec | ❌ Not tested |
| `r210` | Uncompressed RGB 10-bit | ❌ Not tested |
| `rawvideo` | raw video | ❌ Not tested |
| `roq` | id RoQ video (decoders: roqvideo) (encoders: roqvideo) | ❌ Not tested |
| `rpza` | QuickTime video (RPZA) | ❌ Not tested |
| `rv10` | RealVideo 1.0 | ❌ Not tested |
| `rv20` | RealVideo 2.0 | ❌ Not tested |
| `sgi` | SGI image | ❌ Not tested |
| `smc` | QuickTime Graphics (SMC) | ❌ Not tested |
| `snow` | Snow | ❌ Not tested |
| `speedhq` | NewTek SpeedHQ | ❌ Not tested |
| `sunrast` | Sun Rasterfile image | ❌ Not tested |
| `svq1` | Sorenson Vector Quantizer 1 / Sorenson Video 1 / SVQ1 | ❌ Not tested |
| `targa` | Truevision Targa image | ❌ Not tested |
| `tiff` | TIFF image | ❌ Not tested |
| `utvideo` | Ut Video | ❌ Not tested |
| `v210` | Uncompressed 4:2:2 10-bit | ❌ Not tested |
| `v308` | Uncompressed packed 4:4:4 | ❌ Not tested |
| `v408` | Uncompressed packed QT 4:4:4:4 | ❌ Not tested |
| `v410` | Uncompressed 4:4:4 10-bit | ❌ Not tested |
| `vbn` | Vizrt Binary Image | ❌ Not tested |
| `vnull` | Null video codec | ❌ Not tested |
| `wbmp` | WBMP (Wireless Application Protocol Bitmap) image | ❌ Not tested |
| `webp` | WebP (encoders: libwebp_anim libwebp) | ❌ Not tested |
| `wmv1` | Windows Media Video 7 | ❌ Not tested |
| `wmv2` | Windows Media Video 8 | ❌ Not tested |
| `wrapped_avframe` | AVFrame to AVPacket passthrough | ❌ Not tested |
| `xbm` | XBM (X BitMap) image | ❌ Not tested |
| `xface` | X-face image | ❌ Not tested |
| `xwd` | XWD (X Window Dump) image | ❌ Not tested |
| `y41p` | Uncompressed YUV 4:1:1 12-bit | ❌ Not tested |
| `yuv4` | Uncompressed packed 4:2:0 | ❌ Not tested |
| `zlib` | LCL (LossLess Codec Library) ZLIB | ❌ Not tested |
| `zmbv` | Zip Motion Blocks Video | ❌ Not tested |

**Total missing video codecs**: 91

## Missing Audio Codecs

Audio codecs that can be encoded but have not been tested:

| Codec | Description | Status |
|-------|-------------|--------|
| `aac` | AAC (Advanced Audio Coding) (decoders: aac aac_fixed aac_at) (encoders: aac aac_at) | ❌ Not tested |
| `ac3` | ATSC A/52A (AC-3) (decoders: ac3 ac3_fixed ac3_at) (encoders: ac3 ac3_fixed) | ❌ Not tested |
| `adpcm_adx` | SEGA CRI ADX ADPCM | ❌ Not tested |
| `adpcm_argo` | ADPCM Argonaut Games | ❌ Not tested |
| `adpcm_g722` | G.722 ADPCM (decoders: g722) (encoders: g722) | ❌ Not tested |
| `adpcm_g726` | G.726 ADPCM (decoders: g726) (encoders: g726) | ❌ Not tested |
| `adpcm_g726le` | G.726 ADPCM little-endian (decoders: g726le) (encoders: g726le) | ❌ Not tested |
| `adpcm_ima_alp` | ADPCM IMA High Voltage Software ALP | ❌ Not tested |
| `adpcm_ima_amv` | ADPCM IMA AMV | ❌ Not tested |
| `adpcm_ima_apm` | ADPCM IMA Ubisoft APM | ❌ Not tested |
| `adpcm_ima_qt` | ADPCM IMA QuickTime (decoders: adpcm_ima_qt adpcm_ima_qt_at) | ❌ Not tested |
| `adpcm_ima_ssi` | ADPCM IMA Simon & Schuster Interactive | ❌ Not tested |
| `adpcm_ima_wav` | ADPCM IMA WAV | ❌ Not tested |
| `adpcm_ima_ws` | ADPCM IMA Westwood | ❌ Not tested |
| `adpcm_ms` | ADPCM Microsoft | ❌ Not tested |
| `adpcm_swf` | ADPCM Shockwave Flash | ❌ Not tested |
| `adpcm_yamaha` | ADPCM Yamaha | ❌ Not tested |
| `amr_nb` | AMR-NB (Adaptive Multi-Rate NarrowBand) (decoders: amrnb amr_nb_at libopencore_amrnb) (encoders: libopencore_amrnb) | ❌ Not tested |
| `anull` | Null audio codec | ❌ Not tested |
| `aptx` | aptX (Audio Processing Technology for Bluetooth) | ❌ Not tested |
| `aptx_hd` | aptX HD (Audio Processing Technology for Bluetooth) | ❌ Not tested |
| `comfortnoise` | RFC 3389 Comfort Noise | ❌ Not tested |
| `dfpwm` | DFPWM (Dynamic Filter Pulse Width Modulation) | ❌ Not tested |
| `eac3` | ATSC A/52B (AC-3, E-AC-3) (decoders: eac3 eac3_at) | ❌ Not tested |
| `flac` | FLAC (Free Lossless Audio Codec) | ❌ Not tested |
| `g723_1` | G.723.1 | ❌ Not tested |
| `ilbc` | iLBC (Internet Low Bitrate Codec) (decoders: ilbc ilbc_at) (encoders: ilbc_at) | ❌ Not tested |
| `mlp` | MLP (Meridian Lossless Packing) | ❌ Not tested |
| `mp2` | MP2 (MPEG audio layer 2) (decoders: mp2 mp2float mp2_at) (encoders: mp2 mp2fixed) | ❌ Not tested |
| `mp3` | MP3 (MPEG audio layer 3) (decoders: mp3float mp3 mp3_at) (encoders: libmp3lame) | ❌ Not tested |
| `nellymoser` | Nellymoser Asao | ❌ Not tested |
| `opus` | Opus (Opus Interactive Audio Codec) (decoders: opus libopus) (encoders: opus libopus) | ❌ Not tested |
| `pcm_alaw` | PCM A-law / G.711 A-law (decoders: pcm_alaw pcm_alaw_at) (encoders: pcm_alaw pcm_alaw_at) | ❌ Not tested |
| `pcm_bluray` | PCM signed 16|20|24-bit big-endian for Blu-ray media | ❌ Not tested |
| `pcm_dvd` | PCM signed 20|24-bit big-endian | ❌ Not tested |
| `pcm_f32be` | PCM 32-bit floating point big-endian | ❌ Not tested |
| `pcm_f32le` | PCM 32-bit floating point little-endian | ❌ Not tested |
| `pcm_f64be` | PCM 64-bit floating point big-endian | ❌ Not tested |
| `pcm_f64le` | PCM 64-bit floating point little-endian | ❌ Not tested |
| `pcm_mulaw` | PCM mu-law / G.711 mu-law (decoders: pcm_mulaw pcm_mulaw_at) (encoders: pcm_mulaw pcm_mulaw_at) | ❌ Not tested |
| `pcm_s16be` | PCM signed 16-bit big-endian | ❌ Not tested |
| `pcm_s16be_planar` | PCM signed 16-bit big-endian planar | ❌ Not tested |
| `pcm_s16le` | PCM signed 16-bit little-endian | ❌ Not tested |
| `pcm_s16le_planar` | PCM signed 16-bit little-endian planar | ❌ Not tested |
| `pcm_s24be` | PCM signed 24-bit big-endian | ❌ Not tested |
| `pcm_s24daud` | PCM D-Cinema audio signed 24-bit | ❌ Not tested |
| `pcm_s24le` | PCM signed 24-bit little-endian | ❌ Not tested |
| `pcm_s24le_planar` | PCM signed 24-bit little-endian planar | ❌ Not tested |
| `pcm_s32be` | PCM signed 32-bit big-endian | ❌ Not tested |
| `pcm_s32le` | PCM signed 32-bit little-endian | ❌ Not tested |
| `pcm_s32le_planar` | PCM signed 32-bit little-endian planar | ❌ Not tested |
| `pcm_s64be` | PCM signed 64-bit big-endian | ❌ Not tested |
| `pcm_s64le` | PCM signed 64-bit little-endian | ❌ Not tested |
| `pcm_s8` | PCM signed 8-bit | ❌ Not tested |
| `pcm_s8_planar` | PCM signed 8-bit planar | ❌ Not tested |
| `pcm_u16be` | PCM unsigned 16-bit big-endian | ❌ Not tested |
| `pcm_u16le` | PCM unsigned 16-bit little-endian | ❌ Not tested |
| `pcm_u24be` | PCM unsigned 24-bit big-endian | ❌ Not tested |
| `pcm_u24le` | PCM unsigned 24-bit little-endian | ❌ Not tested |
| `pcm_u32be` | PCM unsigned 32-bit big-endian | ❌ Not tested |
| `pcm_u32le` | PCM unsigned 32-bit little-endian | ❌ Not tested |
| `pcm_u8` | PCM unsigned 8-bit | ❌ Not tested |
| `pcm_vidc` | PCM Archimedes VIDC | ❌ Not tested |
| `ra_144` | RealAudio 1.0 (14.4K) (decoders: real_144) (encoders: real_144) | ❌ Not tested |
| `roq_dpcm` | DPCM id RoQ | ❌ Not tested |
| `s302m` | SMPTE 302M | ❌ Not tested |
| `sbc` | SBC (low-complexity subband codec) | ❌ Not tested |
| `speex` | Speex (decoders: speex libspeex) (encoders: libspeex) | ❌ Not tested |
| `truehd` | TrueHD | ❌ Not tested |
| `tta` | TTA (True Audio) | ❌ Not tested |
| `wavpack` | WavPack | ❌ Not tested |
| `wmav1` | Windows Media Audio 1 | ❌ Not tested |
| `wmav2` | Windows Media Audio 2 | ❌ Not tested |

**Total missing audio codecs**: 73

## Missing Pixel Formats

Showing first 50 untested pixel formats (many are esoteric):

| Pixel Format | Status |
|--------------|--------|
| `yuv420p` | ❌ Not tested |
| `yuyv422` | ❌ Not tested |
| `rgb24` | ❌ Not tested |
| `bgr24` | ❌ Not tested |
| `yuv422p` | ❌ Not tested |
| `yuv444p` | ❌ Not tested |
| `yuv410p` | ❌ Not tested |
| `yuv411p` | ❌ Not tested |
| `gray` | ❌ Not tested |
| `yuvj420p` | ❌ Not tested |
| `yuvj422p` | ❌ Not tested |
| `yuvj444p` | ❌ Not tested |
| `uyvy422` | ❌ Not tested |
| `bgr8` | ❌ Not tested |
| `bgr4_byte` | ❌ Not tested |
| `rgb8` | ❌ Not tested |
| `rgb4_byte` | ❌ Not tested |
| `nv12` | ❌ Not tested |
| `nv21` | ❌ Not tested |
| `argb` | ❌ Not tested |
| `rgba` | ❌ Not tested |
| `abgr` | ❌ Not tested |
| `bgra` | ❌ Not tested |
| `gray16be` | ❌ Not tested |
| `gray16le` | ❌ Not tested |
| `yuv440p` | ❌ Not tested |
| `yuvj440p` | ❌ Not tested |
| `yuva420p` | ❌ Not tested |
| `rgb48be` | ❌ Not tested |
| `rgb48le` | ❌ Not tested |
| `rgb565be` | ❌ Not tested |
| `rgb565le` | ❌ Not tested |
| `rgb555be` | ❌ Not tested |
| `rgb555le` | ❌ Not tested |
| `bgr565be` | ❌ Not tested |
| `bgr565le` | ❌ Not tested |
| `bgr555be` | ❌ Not tested |
| `bgr555le` | ❌ Not tested |
| `yuv420p16le` | ❌ Not tested |
| `yuv420p16be` | ❌ Not tested |
| `yuv422p16le` | ❌ Not tested |
| `yuv422p16be` | ❌ Not tested |
| `yuv444p16le` | ❌ Not tested |
| `yuv444p16be` | ❌ Not tested |
| `rgb444le` | ❌ Not tested |
| `rgb444be` | ❌ Not tested |
| `bgr444le` | ❌ Not tested |
| `bgr444be` | ❌ Not tested |
| `ya8` | ❌ Not tested |

**Total missing pixel formats**: 200 (showing first 50)

## RAW Camera Formats (Not in ffprobe)

Camera RAW formats require special handling and cannot be generated with ffmpeg:

| Brand | Extensions | Status |
|-------|------------|--------|
| Canon | .cr2, .cr3, .crw | ❌ Not tested |
| Nikon | .nef, .nrw | ❌ Not tested |
| Sony | .arw, .srf, .sr2 | ❌ Not tested |
| Fujifilm | .raf | ❌ Not tested |
| Olympus | .orf | ❌ Not tested |
| Panasonic | .rw2, .raw | ❌ Not tested |
| Pentax | .pef, .ptx | ❌ Not tested |
| Leica | .rwl, .dng | ❌ Not tested (DNG attempted) |
| Hasselblad | .3fr, .fff | ❌ Not tested |
| Phase One | .iiq | ❌ Not tested |
| Sigma | .x3f | ❌ Not tested |
| Epson | .erf | ❌ Not tested |
| Kodak | .dcr, .kdc | ❌ Not tested |
| Minolta | .mrw | ❌ Not tested |
| Samsung | .srw | ❌ Not tested |

**Note**: RAW formats require actual camera files or specialized converters, cannot be generated synthetically.

## Priority Testing Recommendations

### High Priority (Common Formats)

These are commonly used formats that should be tested:

- Container: `mp4`
- Container: `avi`
- Container: `flv`
- Container: `wmv`
- Container: `mpg`
- Container: `mpeg`
- Container: `3gp`
- Container: `m2ts`
- Container: `ts`
- Container: `mts`
- Container: `vob`
- Container: `f4v`
- Video codec: `mpeg4`
- Video codec: `mpeg2video`
- Video codec: `mpeg1video`
- Video codec: `mjpeg`
- Video codec: `msmpeg4v3`
- Video codec: `wmv2`
- Audio codec: `aac`
- Audio codec: `mp3`

### Medium Priority (Professional/Broadcast)

Professional and broadcast formats:

- `mxf`: ❌ Not tested
- `gxf`: ❌ Not tested
- `lxf`: ❌ Not tested
- `dnxhd`: ✅ Tested
- `prores`: ✅ Tested
- `ffv1`: ❌ Not tested
- `huffyuv`: ❌ Not tested
- `utvideo`: ❌ Not tested
- `cineform`: ❌ Not tested

## Complete Available Formats

### All Muxable Containers (181 total)

| Format | Description |
|--------|-------------|
| ❌ `3g2` | 3GP2 (3GPP2 file format) |
| ❌ `3gp` | 3GP (3GPP file format) |
| ❌ `a64` | a64 - video for Commodore 64 |
| ❌ `ac3` | raw AC-3 |
| ❌ `ac4` | raw AC-4 |
| ❌ `adts` | ADTS AAC (Advanced Audio Coding) |
| ❌ `adx` | CRI ADX |
| ❌ `aea` | MD STUDIO audio |
| ❌ `aiff` | Audio IFF |
| ❌ `alaw` | PCM A-law |
| ❌ `alp` | LEGO Racers ALP |
| ❌ `amr` | 3GPP AMR |
| ❌ `amv` | AMV |
| ❌ `apm` | Ubisoft Rayman 2 APM |
| ❌ `apng` | Animated Portable Network Graphics |
| ❌ `aptx` | raw aptX (Audio Processing Technology for Bluetooth) |
| ❌ `aptx_hd` | raw aptX HD (Audio Processing Technology for Bluetooth) |
| ❌ `apv` | APV raw bitstream |
| ❌ `argo_asf` | Argonaut Games ASF |
| ❌ `argo_cvg` | Argonaut Games CVG |
| ❌ `asf` | ASF (Advanced / Active Streaming Format) |
| ❌ `asf_stream` | ASF (Advanced / Active Streaming Format) |
| ❌ `ass` | SSA (SubStation Alpha) subtitle |
| ❌ `ast` | AST (Audio Stream) |
| ❌ `au` | Sun AU |
| ❌ `avi` | AVI (Audio Video Interleaved) |
| ❌ `avif` | AVIF |
| ❌ `avm2` | SWF (ShockWave Flash) (AVM2) |
| ❌ `avs2` | raw AVS2-P2/IEEE1857.4 video |
| ❌ `avs3` | AVS3-P2/IEEE1857.10 |
| ❌ `bit` | G.729 BIT file format |
| ❌ `caf` | Apple CAF (Core Audio Format) |
| ❌ `cavsvideo` | raw Chinese AVS (Audio Video Standard) video |
| ❌ `codec2` | codec2 .c2 muxer |
| ❌ `codec2raw` | raw codec2 muxer |
| ❌ `crc` | CRC testing |
| ❌ `dash` | DASH Muxer |
| ❌ `data` | raw data |
| ❌ `daud` | D-Cinema audio |
| ❌ `dfpwm` | raw DFPWM1a |
| ❌ `dirac` | raw Dirac |
| ❌ `dnxhd` | raw DNxHD (SMPTE VC-3) |
| ❌ `dts` | raw DTS |
| ❌ `dv` | DV (Digital Video) |
| ❌ `dvd` | MPEG-2 PS (DVD VOB) |
| ❌ `eac3` | raw E-AC-3 |
| ❌ `evc` | raw EVC video |
| ❌ `f32be` | PCM 32-bit floating-point big-endian |
| ❌ `f32le` | PCM 32-bit floating-point little-endian |
| ❌ `f4v` | F4V Adobe Flash Video |
| ❌ `f64be` | PCM 64-bit floating-point big-endian |
| ❌ `f64le` | PCM 64-bit floating-point little-endian |
| ❌ `ffmetadata` | FFmpeg metadata in text |
| ❌ `fifo` | FIFO queue pseudo-muxer |
| ❌ `film_cpk` | Sega FILM / CPK |
| ❌ `filmstrip` | Adobe Filmstrip |
| ❌ `fits` | Flexible Image Transport System |
| ❌ `flac` | raw FLAC |
| ❌ `flv` | FLV (Flash Video) |
| ❌ `framecrc` | framecrc testing |
| ❌ `framehash` | Per-frame hash testing |
| ❌ `framemd5` | Per-frame MD5 testing |
| ❌ `g722` | raw G.722 |
| ❌ `g723_1` | raw G.723.1 |
| ❌ `g726` | raw big-endian G.726 ("left-justified") |
| ❌ `g726le` | raw little-endian G.726 ("right-justified") |
| ❌ `gif` | CompuServe Graphics Interchange Format (GIF) |
| ❌ `gsm` | raw GSM |
| ❌ `gxf` | GXF (General eXchange Format) |
| ❌ `h261` | raw H.261 |
| ❌ `h263` | raw H.263 |
| ❌ `h264` | raw H.264 video |
| ❌ `hash` | Hash testing |
| ❌ `hds` | HDS Muxer |
| ❌ `hevc` | raw HEVC video |
| ❌ `hls` | Apple HTTP Live Streaming |
| ❌ `iamf` | Raw Immersive Audio Model and Formats |
| ❌ `ico` | Microsoft Windows ICO |
| ❌ `ilbc` | iLBC storage |
| ❌ `image2` | image2 sequence |
| ❌ `image2pipe` | piped image2 sequence |
| ❌ `ipod` | iPod H.264 MP4 (MPEG-4 Part 14) |
| ❌ `ircam` | Berkeley/IRCAM/CARL Sound Format |
| ❌ `ismv` | ISMV/ISMA (Smooth Streaming) |
| ❌ `ivf` | On2 IVF |
| ❌ `jacosub` | JACOsub subtitle format |
| ❌ `kvag` | Simon & Schuster Interactive VAG |
| ❌ `latm` | LOAS/LATM |
| ❌ `lc3` | LC3 (Low Complexity Communication Codec) |
| ❌ `lrc` | LRC lyrics |
| ❌ `m4v` | raw MPEG-4 video |
| ❌ `matroska` | Matroska |
| ❌ `mcc` | MacCaption |
| ❌ `md5` | MD5 testing |
| ❌ `microdvd` | MicroDVD subtitle format |
| ❌ `mjpeg` | raw MJPEG video |
| ❌ `mkvtimestamp_v2` | extract pts as timecode v2 format, as defined by mkvtoolnix |
| ❌ `mlp` | raw MLP |
| ❌ `mmf` | Yamaha SMAF |
| ✅ `mov` | QuickTime / MOV |
| ❌ `mp2` | MP2 (MPEG audio layer 2) |
| ❌ `mp3` | MP3 (MPEG audio layer 3) |
| ❌ `mp4` | MP4 (MPEG-4 Part 14) |
| ❌ `mpeg` | MPEG-1 Systems / MPEG program stream |
| ❌ `mpeg1video` | raw MPEG-1 video |
| ❌ `mpeg2video` | raw MPEG-2 video |
| ❌ `mpegts` | MPEG-TS (MPEG-2 Transport Stream) |
| ❌ `mpjpeg` | MIME multipart JPEG |
| ❌ `mulaw` | PCM mu-law |
| ❌ `mxf` | MXF (Material eXchange Format) |
| ❌ `mxf_d10` | MXF (Material eXchange Format) D-10 Mapping |
| ❌ `mxf_opatom` | MXF (Material eXchange Format) Operational Pattern Atom |
| ❌ `null` | raw null video |
| ❌ `nut` | NUT |
| ❌ `obu` | AV1 low overhead OBU |
| ❌ `oga` | Ogg Audio |
| ❌ `ogg` | Ogg |
| ✅ `ogv` | Ogg Video |
| ❌ `oma` | Sony OpenMG audio |
| ❌ `opus` | Ogg Opus |
| ❌ `psp` | PSP MP4 (MPEG-4 Part 14) |
| ❌ `rawvideo` | raw video |
| ❌ `rcwt` | RCWT (Raw Captions With Time) |
| ❌ `rm` | RealMedia |
| ❌ `roq` | raw id RoQ |
| ❌ `rso` | Lego Mindstorms RSO |
| ❌ `rtp` | RTP output |
| ❌ `rtp_mpegts` | RTP/mpegts output format |
| ❌ `rtsp` | RTSP output |
| ❌ `s16be` | PCM signed 16-bit big-endian |
| ❌ `s16le` | PCM signed 16-bit little-endian |
| ❌ `s24be` | PCM signed 24-bit big-endian |
| ❌ `s24le` | PCM signed 24-bit little-endian |
| ❌ `s32be` | PCM signed 32-bit big-endian |
| ❌ `s32le` | PCM signed 32-bit little-endian |
| ❌ `s8` | PCM signed 8-bit |
| ❌ `sap` | SAP output |
| ❌ `sbc` | raw SBC |
| ❌ `scc` | Scenarist Closed Captions |
| ❌ `segment` | segment |
| ❌ `smjpeg` | Loki SDL MJPEG |
| ❌ `smoothstreaming` | Smooth Streaming Muxer |
| ❌ `sox` | SoX (Sound eXchange) native |
| ❌ `spdif` | IEC 61937 (used on S/PDIF - IEC958) |
| ❌ `spx` | Ogg Speex |
| ❌ `srt` | SubRip subtitle |
| ❌ `stream_segment,ssegment` | streaming segment muxer |
| ❌ `streamhash` | Per-stream hash testing |
| ❌ `sup` | raw HDMV Presentation Graphic Stream subtitles |
| ❌ `svcd` | MPEG-2 PS (SVCD) |
| ❌ `swf` | SWF (ShockWave Flash) |
| ❌ `tee` | Multiple muxer tee |
| ❌ `truehd` | raw TrueHD |
| ❌ `tta` | TTA (True Audio) |
| ❌ `ttml` | TTML subtitle |
| ❌ `u16be` | PCM unsigned 16-bit big-endian |
| ❌ `u16le` | PCM unsigned 16-bit little-endian |
| ❌ `u24be` | PCM unsigned 24-bit big-endian |
| ❌ `u24le` | PCM unsigned 24-bit little-endian |
| ❌ `u32be` | PCM unsigned 32-bit big-endian |
| ❌ `u32le` | PCM unsigned 32-bit little-endian |
| ❌ `u8` | PCM unsigned 8-bit |
| ❌ `uncodedframecrc` | uncoded framecrc testing |
| ❌ `vc1` | raw VC-1 video |
| ❌ `vc1test` | VC-1 test bitstream |
| ❌ `vcd` | MPEG-1 Systems / MPEG program stream (VCD) |
| ❌ `vidc` | PCM Archimedes VIDC |
| ❌ `vob` | MPEG-2 PS (VOB) |
| ❌ `voc` | Creative Voice |
| ❌ `vvc` | raw H.266/VVC video |
| ❌ `w64` | Sony Wave64 |
| ❌ `wav` | WAV / WAVE (Waveform Audio) |
| ✅ `webm` | WebM |
| ❌ `webm_chunk` | WebM Chunk Muxer |
| ❌ `webm_dash_manifest` | WebM DASH Manifest |
| ❌ `webp` | WebP |
| ❌ `webvtt` | WebVTT subtitle |
| ❌ `wsaud` | Westwood Studios audio |
| ❌ `wtv` | Windows Television (WTV) |
| ❌ `wv` | raw WavPack |
| ❌ `yuv4mpegpipe` | YUV4MPEG pipe |

### All Encodable Video Codecs (99 total)

| Codec | Description |
|-------|-------------|
| ❌ `a64_multi` | Multicolor charset for Commodore 64 (encoders: a64multi) |
| ❌ `a64_multi5` | Multicolor charset for Commodore 64, extended with 5th color (colram) (encoders: a64multi5) |
| ❌ `alias_pix` | Alias/Wavefront PIX image |
| ❌ `amv` | AMV Video |
| ❌ `apng` | APNG (Animated Portable Network Graphics) image |
| ❌ `asv1` | ASUS V1 |
| ❌ `asv2` | ASUS V2 |
| ✅ `av1` | Alliance for Open Media AV1 (decoders: libdav1d libaom-av1 av1) (encoders: libaom-av1 librav1e libsvtav1) |
| ❌ `avrp` | Avid 1:1 10-bit RGB Packer |
| ❌ `avui` | Avid Meridien Uncompressed |
| ❌ `bitpacked` | Bitpacked |
| ❌ `bmp` | BMP (Windows and OS/2 bitmap) |
| ❌ `cfhd` | GoPro CineForm HD |
| ❌ `cinepak` | Cinepak |
| ❌ `cljr` | Cirrus Logic AccuPak |
| ❌ `dirac` | Dirac (encoders: vc2) |
| ✅ `dnxhd` | VC3/DNxHD |
| ❌ `dpx` | DPX (Digital Picture Exchange) image |
| ❌ `dvvideo` | DV (Digital Video) |
| ❌ `dxv` | Resolume DXV |
| ❌ `exr` | OpenEXR image |
| ❌ `ffv1` | FFmpeg video codec #1 |
| ❌ `ffvhuff` | Huffyuv FFmpeg variant |
| ❌ `fits` | FITS (Flexible Image Transport System) |
| ❌ `flashsv` | Flash Screen Video v1 |
| ❌ `flashsv2` | Flash Screen Video v2 |
| ❌ `flv1` | FLV / Sorenson Spark / Sorenson H.263 (Flash Video) (decoders: flv) (encoders: flv) |
| ❌ `gif` | CompuServe GIF (Graphics Interchange Format) |
| ❌ `h261` | H.261 |
| ❌ `h263` | H.263 / H.263-1996, H.263+ / H.263-1998 / H.263 version 2 |
| ❌ `h263p` | H.263+ / H.263-1998 / H.263 version 2 |
| ✅ `h264` | H.264 / AVC / MPEG-4 AVC / MPEG-4 part 10 (encoders: libx264 libx264rgb h264_videotoolbox) |
| ❌ `hap` | Vidvox Hap |
| ❌ `hdr` | HDR (Radiance RGBE format) image |
| ✅ `hevc` | H.265 / HEVC (High Efficiency Video Coding) (encoders: libx265 hevc_videotoolbox) |
| ❌ `huffyuv` | HuffYUV |
| ❌ `jpeg2000` | JPEG 2000 (encoders: jpeg2000 libopenjpeg) |
| ❌ `jpegls` | JPEG-LS |
| ❌ `jpegxl` | JPEG XL (decoders: libjxl) (encoders: libjxl) |
| ❌ `jpegxl_anim` | JPEG XL animated (decoders: libjxl_anim) (encoders: libjxl_anim) |
| ❌ `ljpeg` | Lossless JPEG |
| ❌ `magicyuv` | MagicYUV video |
| ❌ `mjpeg` | Motion JPEG |
| ❌ `mpeg1video` | MPEG-1 video |
| ❌ `mpeg2video` | MPEG-2 video (decoders: mpeg2video mpegvideo) |
| ❌ `mpeg4` | MPEG-4 part 2 (encoders: mpeg4 libxvid) |
| ❌ `msmpeg4v2` | MPEG-4 part 2 Microsoft variant version 2 |
| ❌ `msmpeg4v3` | MPEG-4 part 2 Microsoft variant version 3 (decoders: msmpeg4) (encoders: msmpeg4) |
| ❌ `msrle` | Microsoft RLE |
| ❌ `msvideo1` | Microsoft Video 1 |
| ❌ `pam` | PAM (Portable AnyMap) image |
| ❌ `pbm` | PBM (Portable BitMap) image |
| ❌ `pcx` | PC Paintbrush PCX image |
| ❌ `pfm` | PFM (Portable FloatMap) image |
| ❌ `pgm` | PGM (Portable GrayMap) image |
| ❌ `pgmyuv` | PGMYUV (Portable GrayMap YUV) image |
| ❌ `phm` | PHM (Portable HalfFloatMap) image |
| ❌ `png` | PNG (Portable Network Graphics) image |
| ❌ `ppm` | PPM (Portable PixelMap) image |
| ✅ `prores` | Apple ProRes (iCodec Pro) (encoders: prores prores_aw prores_ks prores_videotoolbox) |
| ❌ `qoi` | QOI (Quite OK Image) |
| ❌ `qtrle` | QuickTime Animation (RLE) video |
| ❌ `r10k` | AJA Kona 10-bit RGB Codec |
| ❌ `r210` | Uncompressed RGB 10-bit |
| ❌ `rawvideo` | raw video |
| ❌ `roq` | id RoQ video (decoders: roqvideo) (encoders: roqvideo) |
| ❌ `rpza` | QuickTime video (RPZA) |
| ❌ `rv10` | RealVideo 1.0 |
| ❌ `rv20` | RealVideo 2.0 |
| ❌ `sgi` | SGI image |
| ❌ `smc` | QuickTime Graphics (SMC) |
| ❌ `snow` | Snow |
| ❌ `speedhq` | NewTek SpeedHQ |
| ❌ `sunrast` | Sun Rasterfile image |
| ❌ `svq1` | Sorenson Vector Quantizer 1 / Sorenson Video 1 / SVQ1 |
| ❌ `targa` | Truevision Targa image |
| ✅ `theora` | Theora (encoders: libtheora) |
| ❌ `tiff` | TIFF image |
| ❌ `utvideo` | Ut Video |
| ❌ `v210` | Uncompressed 4:2:2 10-bit |
| ❌ `v308` | Uncompressed packed 4:4:4 |
| ❌ `v408` | Uncompressed packed QT 4:4:4:4 |
| ❌ `v410` | Uncompressed 4:4:4 10-bit |
| ❌ `vbn` | Vizrt Binary Image |
| ❌ `vnull` | Null video codec |
| ✅ `vp8` | On2 VP8 (decoders: vp8 libvpx) (encoders: libvpx) |
| ✅ `vp9` | Google VP9 (decoders: vp9 libvpx-vp9) (encoders: libvpx-vp9) |
| ❌ `wbmp` | WBMP (Wireless Application Protocol Bitmap) image |
| ❌ `webp` | WebP (encoders: libwebp_anim libwebp) |
| ❌ `wmv1` | Windows Media Video 7 |
| ❌ `wmv2` | Windows Media Video 8 |
| ❌ `wrapped_avframe` | AVFrame to AVPacket passthrough |
| ❌ `xbm` | XBM (X BitMap) image |
| ❌ `xface` | X-face image |
| ❌ `xwd` | XWD (X Window Dump) image |
| ❌ `y41p` | Uncompressed YUV 4:1:1 12-bit |
| ❌ `yuv4` | Uncompressed packed 4:2:0 |
| ❌ `zlib` | LCL (LossLess Codec Library) ZLIB |
| ❌ `zmbv` | Zip Motion Blocks Video |

### All Encodable Audio Codecs (76 total)

| Codec | Description |
|-------|-------------|
| ❌ `aac` | AAC (Advanced Audio Coding) (decoders: aac aac_fixed aac_at) (encoders: aac aac_at) |
| ❌ `ac3` | ATSC A/52A (AC-3) (decoders: ac3 ac3_fixed ac3_at) (encoders: ac3 ac3_fixed) |
| ❌ `adpcm_adx` | SEGA CRI ADX ADPCM |
| ❌ `adpcm_argo` | ADPCM Argonaut Games |
| ❌ `adpcm_g722` | G.722 ADPCM (decoders: g722) (encoders: g722) |
| ❌ `adpcm_g726` | G.726 ADPCM (decoders: g726) (encoders: g726) |
| ❌ `adpcm_g726le` | G.726 ADPCM little-endian (decoders: g726le) (encoders: g726le) |
| ❌ `adpcm_ima_alp` | ADPCM IMA High Voltage Software ALP |
| ❌ `adpcm_ima_amv` | ADPCM IMA AMV |
| ❌ `adpcm_ima_apm` | ADPCM IMA Ubisoft APM |
| ❌ `adpcm_ima_qt` | ADPCM IMA QuickTime (decoders: adpcm_ima_qt adpcm_ima_qt_at) |
| ❌ `adpcm_ima_ssi` | ADPCM IMA Simon & Schuster Interactive |
| ❌ `adpcm_ima_wav` | ADPCM IMA WAV |
| ❌ `adpcm_ima_ws` | ADPCM IMA Westwood |
| ❌ `adpcm_ms` | ADPCM Microsoft |
| ❌ `adpcm_swf` | ADPCM Shockwave Flash |
| ❌ `adpcm_yamaha` | ADPCM Yamaha |
| ✅ `alac` | ALAC (Apple Lossless Audio Codec) (decoders: alac alac_at) (encoders: alac alac_at) |
| ❌ `amr_nb` | AMR-NB (Adaptive Multi-Rate NarrowBand) (decoders: amrnb amr_nb_at libopencore_amrnb) (encoders: libopencore_amrnb) |
| ❌ `anull` | Null audio codec |
| ❌ `aptx` | aptX (Audio Processing Technology for Bluetooth) |
| ❌ `aptx_hd` | aptX HD (Audio Processing Technology for Bluetooth) |
| ❌ `comfortnoise` | RFC 3389 Comfort Noise |
| ❌ `dfpwm` | DFPWM (Dynamic Filter Pulse Width Modulation) |
| ✅ `dts` | DCA (DTS Coherent Acoustics) (decoders: dca) (encoders: dca) |
| ❌ `eac3` | ATSC A/52B (AC-3, E-AC-3) (decoders: eac3 eac3_at) |
| ❌ `flac` | FLAC (Free Lossless Audio Codec) |
| ❌ `g723_1` | G.723.1 |
| ❌ `ilbc` | iLBC (Internet Low Bitrate Codec) (decoders: ilbc ilbc_at) (encoders: ilbc_at) |
| ❌ `mlp` | MLP (Meridian Lossless Packing) |
| ❌ `mp2` | MP2 (MPEG audio layer 2) (decoders: mp2 mp2float mp2_at) (encoders: mp2 mp2fixed) |
| ❌ `mp3` | MP3 (MPEG audio layer 3) (decoders: mp3float mp3 mp3_at) (encoders: libmp3lame) |
| ❌ `nellymoser` | Nellymoser Asao |
| ❌ `opus` | Opus (Opus Interactive Audio Codec) (decoders: opus libopus) (encoders: opus libopus) |
| ❌ `pcm_alaw` | PCM A-law / G.711 A-law (decoders: pcm_alaw pcm_alaw_at) (encoders: pcm_alaw pcm_alaw_at) |
| ❌ `pcm_bluray` | PCM signed 16|20|24-bit big-endian for Blu-ray media |
| ❌ `pcm_dvd` | PCM signed 20|24-bit big-endian |
| ❌ `pcm_f32be` | PCM 32-bit floating point big-endian |
| ❌ `pcm_f32le` | PCM 32-bit floating point little-endian |
| ❌ `pcm_f64be` | PCM 64-bit floating point big-endian |
| ❌ `pcm_f64le` | PCM 64-bit floating point little-endian |
| ❌ `pcm_mulaw` | PCM mu-law / G.711 mu-law (decoders: pcm_mulaw pcm_mulaw_at) (encoders: pcm_mulaw pcm_mulaw_at) |
| ❌ `pcm_s16be` | PCM signed 16-bit big-endian |
| ❌ `pcm_s16be_planar` | PCM signed 16-bit big-endian planar |
| ❌ `pcm_s16le` | PCM signed 16-bit little-endian |
| ❌ `pcm_s16le_planar` | PCM signed 16-bit little-endian planar |
| ❌ `pcm_s24be` | PCM signed 24-bit big-endian |
| ❌ `pcm_s24daud` | PCM D-Cinema audio signed 24-bit |
| ❌ `pcm_s24le` | PCM signed 24-bit little-endian |
| ❌ `pcm_s24le_planar` | PCM signed 24-bit little-endian planar |
| ❌ `pcm_s32be` | PCM signed 32-bit big-endian |
| ❌ `pcm_s32le` | PCM signed 32-bit little-endian |
| ❌ `pcm_s32le_planar` | PCM signed 32-bit little-endian planar |
| ❌ `pcm_s64be` | PCM signed 64-bit big-endian |
| ❌ `pcm_s64le` | PCM signed 64-bit little-endian |
| ❌ `pcm_s8` | PCM signed 8-bit |
| ❌ `pcm_s8_planar` | PCM signed 8-bit planar |
| ❌ `pcm_u16be` | PCM unsigned 16-bit big-endian |
| ❌ `pcm_u16le` | PCM unsigned 16-bit little-endian |
| ❌ `pcm_u24be` | PCM unsigned 24-bit big-endian |
| ❌ `pcm_u24le` | PCM unsigned 24-bit little-endian |
| ❌ `pcm_u32be` | PCM unsigned 32-bit big-endian |
| ❌ `pcm_u32le` | PCM unsigned 32-bit little-endian |
| ❌ `pcm_u8` | PCM unsigned 8-bit |
| ❌ `pcm_vidc` | PCM Archimedes VIDC |
| ❌ `ra_144` | RealAudio 1.0 (14.4K) (decoders: real_144) (encoders: real_144) |
| ❌ `roq_dpcm` | DPCM id RoQ |
| ❌ `s302m` | SMPTE 302M |
| ❌ `sbc` | SBC (low-complexity subband codec) |
| ❌ `speex` | Speex (decoders: speex libspeex) (encoders: libspeex) |
| ❌ `truehd` | TrueHD |
| ❌ `tta` | TTA (True Audio) |
| ✅ `vorbis` | Vorbis (decoders: vorbis libvorbis) (encoders: vorbis libvorbis) |
| ❌ `wavpack` | WavPack |
| ❌ `wmav1` | Windows Media Audio 1 |
| ❌ `wmav2` | Windows Media Audio 2 |

---

*Generated by analyze_missing_formats.py*