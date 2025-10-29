# Format Registry - Unified Naming System

**Universal format identifier mapping across all detection tools**

This registry provides a unified naming system for media formats, codecs, and related attributes. Each format is assigned a unique UUID that maps to tool-specific names used by different detection libraries.

## Purpose

Different detection tools use different names for the same formats:
- `ffprobe` might call it `h264`
- `libmagic` might detect it as `MPEG v4 system`
- `puremagic` returns `video/mp4` (MIME type)
- `exiftool` reports it as `AVC`

This registry resolves these naming conflicts by providing:
1. **UUID**: Globally unique identifier (deterministic, reproducible)
2. **Canonical Name**: Standard internal name for Smart Media Manager
3. **Tool-specific mappings**: What each tool calls this format

## Detection Tools

| Tool | Description | Used For |
|------|-------------|----------|
| **ffprobe** | FFmpeg's format probe | Containers, codecs, pixel/sample formats, layouts |
| **libmagic** | File type identification (via python-magic) | File signatures, MIME types |
| **puremagic** | Pure Python magic number detection | File signatures without libmagic |
| **pyfsig** | Python file signature library | Additional format signatures |
| **binwalk** | Firmware analysis tool | Binary signature scanning |
| **rawpy** | RAW image processing (libraw wrapper) | Camera RAW formats |
| **Pillow** | Python Imaging Library | Image format processing |
| **exiftool** | Metadata extraction | Format identification from metadata |

## Format Categories

### Container Formats

| UUID (Type-Suffixed) | Canonical Name | ffprobe | libmagic | puremagic | pyfsig | binwalk | rawpy | Pillow | exiftool |
|---------------------|---------------|---------|----------|-----------|--------|---------|-------|--------|----------|
| `40fcd791...-C` | **3dostr** | 3dostr | — | — | — | — | — | — | — |
| `093583c1...-C` | **3g2** | 3g2 | — | — | — | — | — | — | — |
| `84d2205f...-C` | **3gp** | 3gp | — | — | — | — | — | — | — |
| `f2f5f78a...-C` | **4xm** | 4xm | — | — | — | — | — | — | — |
| `f578d3a9...-C` | **a64** | a64 | — | — | — | — | — | — | — |
| `1157f31d...-C` | **aa** | aa | — | — | — | — | — | — | — |
| `458ed14d...-C` | **aac** | aac | — | — | — | — | — | — | — |
| `b530501d...-C` | **aax** | aax | — | — | — | — | — | — | — |
| `50f7d473...-C` | **ac3** | ac3 | — | — | — | — | — | — | — |
| `68f9acfa...-C` | **ac4** | ac4 | — | — | — | — | — | — | — |
| `7e94db15...-C` | **ace** | ace | — | — | — | — | — | — | — |
| `cedaf28b...-C` | **acm** | acm | — | — | — | — | — | — | — |
| `3adf5932...-C` | **act** | act | — | — | — | — | — | — | — |
| `45e4ac25...-C` | **adf** | adf | — | — | — | — | — | — | — |
| `81628ae6...-C` | **adp** | adp | — | — | — | — | — | — | — |
| `6f9cb1d7...-C` | **ads** | ads | — | — | — | — | — | — | — |
| `17c9dafe...-C` | **adts** | adts | — | — | — | — | — | — | — |
| `e0836bd1...-C` | **adx** | adx | — | — | — | — | — | — | — |
| `7ae3a862...-C` | **aea** | aea | — | — | — | — | — | — | — |
| `72519a24...-C` | **afc** | afc | — | — | — | — | — | — | — |
| `6ef0d275...-C` | **aiff** | aiff | — | — | — | — | — | — | — |
| `5f9e5eb3...-C` | **aix** | aix | — | — | — | — | — | — | — |
| `5b313ba8...-C` | **alaw** | alaw | — | — | — | — | — | — | — |
| `d3fde19d...-C` | **alias_pix** | alias_pix | — | — | — | — | — | — | — |
| `5b4e0fc0...-C` | **alp** | alp | — | — | — | — | — | — | — |
| `af78d65e...-C` | **amr** | amr | — | — | — | — | — | — | — |
| `235eed17...-C` | **amrnb** | amrnb | — | — | — | — | — | — | — |
| `adc89d46...-C` | **amrwb** | amrwb | — | — | — | — | — | — | — |
| `ec731d26...-C` | **amv** | amv | — | — | — | — | — | — | — |
| `346c0137...-C` | **anm** | anm | — | — | — | — | — | — | — |
| `526b9cd2...-C` | **apac** | apac | — | — | — | — | — | — | — |
| `c6e453be...-C` | **apc** | apc | — | — | — | — | — | — | — |
| `115cae10...-C` | **ape** | ape | — | — | — | — | — | — | — |
| `8d1fdcbc...-C` | **apm** | apm | — | — | — | — | — | — | — |
| `551a7fed...-C` | **apng** | apng | — | — | — | — | — | — | — |
| `8caebe0d...-C` | **aptx** | aptx | — | — | — | — | — | — | — |
| `d7b2fd94...-C` | **aptx_hd** | aptx_hd | — | — | — | — | — | — | — |
| `f11b76d1...-C` | **apv** | apv | — | — | — | — | — | — | — |
| `46ab3f2c...-C` | **aqtitle** | aqtitle | — | — | — | — | — | — | — |
| `ed37289d...-C` | **argo_asf** | argo_asf | — | — | — | — | — | — | — |
| `62f6a35d...-C` | **argo_brp** | argo_brp | — | — | — | — | — | — | — |
| `a2c131ca...-C` | **argo_cvg** | argo_cvg | — | — | — | — | — | — | — |
| `7f630cd5...-C` | **asf** | asf | — | — | — | — | — | — | — |
| `2b6395b9...-C` | **asf_o** | asf_o | — | — | — | — | — | — | — |
| `2aac53d3...-C` | **asf_stream** | asf_stream | — | — | — | — | — | — | — |
| `4a6aca20...-C` | **ass** | ass | — | — | — | — | — | — | — |
| `cde169a2...-C` | **ast** | ast | — | — | — | — | — | — | — |
| `31e56ccc...-C` | **au** | au | — | — | — | — | — | — | — |
| `bc40c757...-C` | **av1** | av1 | ISO Media | video/mp4 | — | — | — | N/A | AV1 |
| `c7fd4386...-C` | **avi** | avi | RIFF (little-endian) data, AVI | video/x-msvideo | — | — | — | N/A | AVI |
| `2f6ae690...-C` | **avif** | avif | ISO Media | image/avif | — | — | — | AVIF | AVIF |
| `d8a8630c...-C` | **avm2** | avm2 | — | — | — | — | — | — | — |
| `a157a83b...-C` | **avr** | avr | — | — | — | — | — | — | — |
| `dbc846d9...-C` | **avs** | avs | — | — | — | — | — | — | — |
| `71ee3b3f...-C` | **avs2** | avs2 | — | — | — | — | — | — | — |
| `2e8de15b...-C` | **avs3** | avs3 | — | — | — | — | — | — | — |
| `2db10a7b...-C` | **bethsoftvid** | bethsoftvid | — | — | — | — | — | — | — |
| `4ce63896...-C` | **bfi** | bfi | — | — | — | — | — | — | — |
| `3e5cbbcb...-C` | **bfstm** | bfstm | — | — | — | — | — | — | — |
| `1fb786d8...-C` | **bin** | bin | — | — | — | — | — | — | — |
| `21248660...-C` | **bink** | bink | — | — | — | — | — | — | — |
| `afbe6df4...-C` | **binka** | binka | — | — | — | — | — | — | — |
| `a49c45cf...-C` | **bit** | bit | — | — | — | — | — | — | — |
| `1cdd3f54...-C` | **bitpacked** | bitpacked | — | — | — | — | — | — | — |
| `6254e908...-C` | **bmp_pipe** | bmp_pipe | — | — | — | — | — | — | — |
| `b7c9db34...-C` | **bmv** | bmv | — | — | — | — | — | — | — |
| `c1393756...-C` | **boa** | boa | — | — | — | — | — | — | — |
| `58eb151e...-C` | **bonk** | bonk | — | — | — | — | — | — | — |
| `76b546b5...-C` | **brender_pix** | brender_pix | — | — | — | — | — | — | — |
| `7a730854...-C` | **brstm** | brstm | — | — | — | — | — | — | — |
| `c1696193...-C` | **c93** | c93 | — | — | — | — | — | — | — |
| `74fd0a26...-C` | **caf** | caf | — | — | — | — | — | — | — |
| `9d414937...-C` | **cavsvideo** | cavsvideo | — | — | — | — | — | — | — |
| `e92865b8...-C` | **cdg** | cdg | — | — | — | — | — | — | — |
| `8137661d...-C` | **cdxl** | cdxl | — | — | — | — | — | — | — |
| `fb566510...-C` | **cine** | cine | — | — | — | — | — | — | — |
| `c7602580...-C` | **codec2** | codec2 | — | — | — | — | — | — | — |
| `b238b2bc...-C` | **codec2raw** | codec2raw | — | — | — | — | — | — | — |
| `a499ab45...-C` | **concat** | concat | — | — | — | — | — | — | — |
| `42f95fa4...-C` | **crc** | crc | — | — | — | — | — | — | — |
| `3964eaa3...-C` | **cri_pipe** | cri_pipe | — | — | — | — | — | — | — |
| `ad5f5e58...-C` | **dash** | dash | — | — | — | — | — | — | — |
| `1d281805...-C` | **data** | data | — | — | — | — | — | — | — |
| `03b03c45...-C` | **daud** | daud | — | — | — | — | — | — | — |
| `dc18cfbf...-C` | **dcstr** | dcstr | — | — | — | — | — | — | — |
| `23f732fc...-C` | **dds_pipe** | dds_pipe | — | — | — | — | — | — | — |
| `74a6ac7a...-C` | **derf** | derf | — | — | — | — | — | — | — |
| `74f3b48e...-C` | **dfa** | dfa | — | — | — | — | — | — | — |
| `92e05a5c...-C` | **dfpwm** | dfpwm | — | — | — | — | — | — | — |
| `39095877...-C` | **dhav** | dhav | — | — | — | — | — | — | — |
| `48832084...-C` | **dirac** | dirac | — | — | — | — | — | — | — |
| `74c11481...-C` | **dnxhd** | dnxhd | — | — | — | — | — | — | — |
| `74e108b7...-C` | **dpx_pipe** | dpx_pipe | — | — | — | — | — | — | — |
| `63b3f7b9...-C` | **dsf** | dsf | — | — | — | — | — | — | — |
| `af77a0cb...-C` | **dsicin** | dsicin | — | — | — | — | — | — | — |
| `f727aabd...-C` | **dss** | dss | — | — | — | — | — | — | — |
| `7a7276a5...-C` | **dts** | dts | — | — | — | — | — | — | — |
| `5dd947c2...-C` | **dtshd** | dtshd | — | — | — | — | — | — | — |
| `ded71677...-C` | **dv** | dv | — | — | — | — | — | — | — |
| `017c0a52...-C` | **dvbsub** | dvbsub | — | — | — | — | — | — | — |
| `b9d61a31...-C` | **dvbtxt** | dvbtxt | — | — | — | — | — | — | — |
| `e23f2f57...-C` | **dvd** | dvd | — | — | — | — | — | — | — |
| `6e8a6c82...-C` | **dxa** | dxa | — | — | — | — | — | — | — |
| `fae217fd...-C` | **ea** | ea | — | — | — | — | — | — | — |
| `ca8a8662...-C` | **ea_cdata** | ea_cdata | — | — | — | — | — | — | — |
| `1dd0b283...-C` | **eac3** | eac3 | — | — | — | — | — | — | — |
| `09f5e04a...-C` | **epaf** | epaf | — | — | — | — | — | — | — |
| `f2674f95...-C` | **evc** | evc | — | — | — | — | — | — | — |
| `11468e1f...-C` | **exr_pipe** | exr_pipe | — | — | — | — | — | — | — |
| `de9b272f...-C` | **f32be** | f32be | — | — | — | — | — | — | — |
| `93f93bd8...-C` | **f32le** | f32le | — | — | — | — | — | — | — |
| `9dc3da9d...-C` | **f4v** | f4v | — | — | — | — | — | — | — |
| `a2c3dd12...-C` | **f64be** | f64be | — | — | — | — | — | — | — |
| `67214b6a...-C` | **f64le** | f64le | — | — | — | — | — | — | — |
| `1322cb66...-C` | **ffmetadata** | ffmetadata | — | — | — | — | — | — | — |
| `fb8d3259...-C` | **fifo** | fifo | — | — | — | — | — | — | — |
| `8ef008a2...-C` | **film_cpk** | film_cpk | — | — | — | — | — | — | — |
| `c67a469a...-C` | **filmstrip** | filmstrip | — | — | — | — | — | — | — |
| `bd12d03b...-C` | **fits** | fits | — | — | — | — | — | — | — |
| `bf744455...-C` | **flac** | flac | — | — | — | — | — | — | — |
| `8cbe5947...-C` | **flic** | flic | — | — | — | — | — | — | — |
| `9127bc49...-C` | **flv** | flv | — | — | — | — | — | — | — |
| `a91ce192...-C` | **framecrc** | framecrc | — | — | — | — | — | — | — |
| `c3c1ad8e...-C` | **framehash** | framehash | — | — | — | — | — | — | — |
| `3e37a0e9...-C` | **framemd5** | framemd5 | — | — | — | — | — | — | — |
| `59315f29...-C` | **frm** | frm | — | — | — | — | — | — | — |
| `171d64e3...-C` | **fsb** | fsb | — | — | — | — | — | — | — |
| `70d4ec7b...-C` | **fwse** | fwse | — | — | — | — | — | — | — |
| `c3997b9a...-C` | **g722** | g722 | — | — | — | — | — | — | — |
| `8765e7e1...-C` | **g723_1** | g723_1 | — | — | — | — | — | — | — |
| `cc3e176b...-C` | **g726** | g726 | — | — | — | — | — | — | — |
| `08f389d7...-C` | **g726le** | g726le | — | — | — | — | — | — | — |
| `2f59e7ce...-C` | **g728** | g728 | — | — | — | — | — | — | — |
| `32d26757...-C` | **g729** | g729 | — | — | — | — | — | — | — |
| `9cc60da8...-C` | **gdv** | gdv | — | — | — | — | — | — | — |
| `2b17ad4e...-C` | **gem_pipe** | gem_pipe | — | — | — | — | — | — | — |
| `ba93a271...-C` | **genh** | genh | — | — | — | — | — | — | — |
| `80645058...-C` | **gif_pipe** | gif_pipe | — | — | — | — | — | — | — |
| `095e1cab...-C` | **gsm** | gsm | — | — | — | — | — | — | — |
| `676d5e79...-C` | **gxf** | gxf | — | — | — | — | — | — | — |
| `751b9707...-C` | **h261** | h261 | — | — | — | — | — | — | — |
| `6e20a312...-C` | **h263** | h263 | — | — | — | — | — | — | — |
| `d6ea65a0...-C` | **h264** | h264 | MPEG v4 system | video/mp4 | — | — | — | N/A | AVC |
| `adac47a7...-C` | **hash** | hash | — | — | — | — | — | — | — |
| `698ef80b...-C` | **hca** | hca | — | — | — | — | — | — | — |
| `fde8de79...-C` | **hcom** | hcom | — | — | — | — | — | — | — |
| `c874e9e6...-C` | **hdr_pipe** | hdr_pipe | — | — | — | — | — | — | — |
| `aaa6c97a...-C` | **hds** | hds | — | — | — | — | — | — | — |
| `4aa64d23...-C` | **hevc** | hevc | ISO Media | video/mp4 | — | — | — | N/A | HEVC |
| `2408a626...-C` | **hls** | hls | — | — | — | — | — | — | — |
| `85423c91...-C` | **hnm** | hnm | — | — | — | — | — | — | — |
| `d2520a8c...-C` | **iamf** | iamf | — | — | — | — | — | — | — |
| `251d95c9...-C` | **ico** | ico | — | — | — | — | — | — | — |
| `2dd7b22f...-C` | **idcin** | idcin | — | — | — | — | — | — | — |
| `33940393...-C` | **idf** | idf | — | — | — | — | — | — | — |
| `f4dff553...-C` | **iff** | iff | — | — | — | — | — | — | — |
| `f44051da...-C` | **ifv** | ifv | — | — | — | — | — | — | — |
| `4a9cee6e...-C` | **ilbc** | ilbc | — | — | — | — | — | — | — |
| `52c9f5e1...-C` | **image2** | image2 | — | — | — | — | — | — | — |
| `ac0df839...-C` | **image2pipe** | image2pipe | — | — | — | — | — | — | — |
| `e02de780...-C` | **imf** | imf | — | — | — | — | — | — | — |
| `eaa626ae...-C` | **ingenient** | ingenient | — | — | — | — | — | — | — |
| `7fb1385c...-C` | **ipmovie** | ipmovie | — | — | — | — | — | — | — |
| `e090f758...-C` | **ipod** | ipod | — | — | — | — | — | — | — |
| `71903719...-C` | **ipu** | ipu | — | — | — | — | — | — | — |
| `d64a27cb...-C` | **ircam** | ircam | — | — | — | — | — | — | — |
| `f9debd09...-C` | **ismv** | ismv | — | — | — | — | — | — | — |
| `42ded3bf...-C` | **iss** | iss | — | — | — | — | — | — | — |
| `f909600e...-C` | **iv8** | iv8 | — | — | — | — | — | — | — |
| `89d5c5a7...-C` | **ivf** | ivf | — | — | — | — | — | — | — |
| `e1918d9b...-C` | **ivr** | ivr | — | — | — | — | — | — | — |
| `02782949...-C` | **j2k_pipe** | j2k_pipe | — | — | — | — | — | — | — |
| `8910696a...-C` | **jacosub** | jacosub | — | — | — | — | — | — | — |
| `4c51fe44...-C` | **jpeg_pipe** | jpeg_pipe | — | — | — | — | — | — | — |
| `c227e463...-C` | **jpegls_pipe** | jpegls_pipe | — | — | — | — | — | — | — |
| `f028add4...-C` | **jpegxl_anim** | jpegxl_anim | — | — | — | — | — | — | — |
| `6d64a899...-C` | **jpegxl_pipe** | jpegxl_pipe | — | — | — | — | — | — | — |
| `fe716ed5...-C` | **jv** | jv | — | — | — | — | — | — | — |
| `3f9cf970...-C` | **kux** | kux | — | — | — | — | — | — | — |
| `e57642c0...-C` | **kvag** | kvag | — | — | — | — | — | — | — |
| `c8566b86...-C` | **laf** | laf | — | — | — | — | — | — | — |
| `3af8f743...-C` | **latm** | latm | — | — | — | — | — | — | — |
| `15a8172f...-C` | **lc3** | lc3 | — | — | — | — | — | — | — |
| `5c9e3ac0...-C` | **live_flv** | live_flv | — | — | — | — | — | — | — |
| `5ce2d4d3...-C` | **lmlm4** | lmlm4 | — | — | — | — | — | — | — |
| `3c0d176c...-C` | **loas** | loas | — | — | — | — | — | — | — |
| `0973adb4...-C` | **lrc** | lrc | — | — | — | — | — | — | — |
| `6b1c67bd...-C` | **luodat** | luodat | — | — | — | — | — | — | — |
| `078af735...-C` | **lvf** | lvf | — | — | — | — | — | — | — |
| `f33ffc39...-C` | **lxf** | lxf | — | — | — | — | — | — | — |
| `eeca0b04...-C` | **m4v** | m4v | — | — | — | — | — | — | — |
| `2a465d03...-C` | **matroska** | matroska | — | — | — | — | — | — | — |
| `3329a0a3...-C` | **matroska,webm** | matroska,webm | — | — | — | — | — | — | — |
| `1d4e99ce...-C` | **mca** | mca | — | — | — | — | — | — | — |
| `0c7deaf4...-C` | **mcc** | mcc | — | — | — | — | — | — | — |
| `98f2297a...-C` | **md5** | md5 | — | — | — | — | — | — | — |
| `db15bd06...-C` | **mgsts** | mgsts | — | — | — | — | — | — | — |
| `0a71b86b...-C` | **microdvd** | microdvd | — | — | — | — | — | — | — |
| `f6a88d38...-C` | **mjpeg** | mjpeg | — | — | — | — | — | — | — |
| `bf7f3b3e...-C` | **mjpeg_2000** | mjpeg_2000 | — | — | — | — | — | — | — |
| `fb79e10b...-C` | **mkvtimestamp_v2** | mkvtimestamp_v2 | — | — | — | — | — | — | — |
| `b2364ba9...-C` | **mlp** | mlp | — | — | — | — | — | — | — |
| `ef5d93ea...-C` | **mlv** | mlv | — | — | — | — | — | — | — |
| `73581bd2...-C` | **mm** | mm | — | — | — | — | — | — | — |
| `f1b513a9...-C` | **mmf** | mmf | — | — | — | — | — | — | — |
| `140323aa...-C` | **mods** | mods | — | — | — | — | — | — | — |
| `672f1b78...-C` | **moflex** | moflex | — | — | — | — | — | — | — |
| `3f8a2874...-C` | **mov** | mov | ISO Media, Apple QuickTime | video/quicktime | — | — | — | N/A | QuickTime |
| `759bb7b6...-C` | **mov,mp4,m4a,3gp,3g2,mj2** | mov,mp4,m4a,3gp,3g2,mj2 | — | — | — | — | — | — | — |
| `053b33fb...-C` | **mp2** | mp2 | — | — | — | — | — | — | — |
| `0ca0edce...-C` | **mp3** | mp3 | — | — | — | — | — | — | — |
| `a9457602...-C` | **mp4** | mp4 | ISO Media, MP4 | video/mp4 | — | — | — | N/A | MP4 |
| `8940cfbe...-C` | **mpc** | mpc | — | — | — | — | — | — | — |
| `e09dd7c3...-C` | **mpc8** | mpc8 | — | — | — | — | — | — | — |
| `64232332...-C` | **mpeg** | mpeg | — | — | — | — | — | — | — |
| `661339ba...-C` | **mpeg1video** | mpeg1video | — | — | — | — | — | — | — |
| `7dabad2b...-C` | **mpeg2video** | mpeg2video | — | — | — | — | — | — | — |
| `64d1e20d...-C` | **mpegts** | mpegts | — | — | — | — | — | — | — |
| `2c25d300...-C` | **mpegtsraw** | mpegtsraw | — | — | — | — | — | — | — |
| `b4e7232c...-C` | **mpegvideo** | mpegvideo | — | — | — | — | — | — | — |
| `82780d05...-C` | **mpjpeg** | mpjpeg | — | — | — | — | — | — | — |
| `c11d99ef...-C` | **mpl2** | mpl2 | — | — | — | — | — | — | — |
| `d964dcaa...-C` | **mpsub** | mpsub | — | — | — | — | — | — | — |
| `0211f0b7...-C` | **msf** | msf | — | — | — | — | — | — | — |
| `7e929e6b...-C` | **msnwctcp** | msnwctcp | — | — | — | — | — | — | — |
| `12528eba...-C` | **msp** | msp | — | — | — | — | — | — | — |
| `1dafdb92...-C` | **mtaf** | mtaf | — | — | — | — | — | — | — |
| `cdb888a7...-C` | **mtv** | mtv | — | — | — | — | — | — | — |
| `6bfa7edf...-C` | **mulaw** | mulaw | — | — | — | — | — | — | — |
| `b4f8133e...-C` | **musx** | musx | — | — | — | — | — | — | — |
| `e8635cfa...-C` | **mv** | mv | — | — | — | — | — | — | — |
| `0755b281...-C` | **mvi** | mvi | — | — | — | — | — | — | — |
| `f11cebfe...-C` | **mxf** | mxf | — | — | — | — | — | — | — |
| `6265a217...-C` | **mxf_d10** | mxf_d10 | — | — | — | — | — | — | — |
| `824b66ea...-C` | **mxf_opatom** | mxf_opatom | — | — | — | — | — | — | — |
| `167fdf5f...-C` | **mxg** | mxg | — | — | — | — | — | — | — |
| `dfce1cd2...-C` | **nc** | nc | — | — | — | — | — | — | — |
| `a794982e...-C` | **nistsphere** | nistsphere | — | — | — | — | — | — | — |
| `b7da877e...-C` | **nsp** | nsp | — | — | — | — | — | — | — |
| `f8f9754f...-C` | **nsv** | nsv | — | — | — | — | — | — | — |
| `46c227c2...-C` | **null** | null | — | — | — | — | — | — | — |
| `1b232105...-C` | **nut** | nut | — | — | — | — | — | — | — |
| `f7bb07f1...-C` | **nuv** | nuv | — | — | — | — | — | — | — |
| `4a188339...-C` | **obu** | obu | — | — | — | — | — | — | — |
| `ab7765ba...-C` | **oga** | oga | — | — | — | — | — | — | — |
| `d3238328...-C` | **ogg** | ogg | — | — | — | — | — | — | — |
| `f291a488...-C` | **ogv** | ogv | — | — | — | — | — | — | — |
| `efd4e2cc...-C` | **oma** | oma | — | — | — | — | — | — | — |
| `447f60b1...-C` | **opus** | opus | — | — | — | — | — | — | — |
| `9fcdf8b6...-C` | **osq** | osq | — | — | — | — | — | — | — |
| `80dc11c9...-C` | **paf** | paf | — | — | — | — | — | — | — |
| `76511930...-C` | **pam_pipe** | pam_pipe | — | — | — | — | — | — | — |
| `c2dd3d19...-C` | **pbm_pipe** | pbm_pipe | — | — | — | — | — | — | — |
| `b4e4fd2b...-C` | **pcx_pipe** | pcx_pipe | — | — | — | — | — | — | — |
| `9ef7fc47...-C` | **pdv** | pdv | — | — | — | — | — | — | — |
| `5f4db972...-C` | **pfm_pipe** | pfm_pipe | — | — | — | — | — | — | — |
| `f4c8ce00...-C` | **pgm_pipe** | pgm_pipe | — | — | — | — | — | — | — |
| `4a367e7b...-C` | **pgmyuv_pipe** | pgmyuv_pipe | — | — | — | — | — | — | — |
| `0abffa86...-C` | **pgx_pipe** | pgx_pipe | — | — | — | — | — | — | — |
| `c3aa16a3...-C` | **phm_pipe** | phm_pipe | — | — | — | — | — | — | — |
| `3ea52f3c...-C` | **photocd_pipe** | photocd_pipe | — | — | — | — | — | — | — |
| `aaf9a2ce...-C` | **pictor_pipe** | pictor_pipe | — | — | — | — | — | — | — |
| `7ffbf711...-C` | **pjs** | pjs | — | — | — | — | — | — | — |
| `508a328b...-C` | **pmp** | pmp | — | — | — | — | — | — | — |
| `5039ee0f...-C` | **png_pipe** | png_pipe | — | — | — | — | — | — | — |
| `04beb324...-C` | **pp_bnk** | pp_bnk | — | — | — | — | — | — | — |
| `c98bba6d...-C` | **ppm_pipe** | ppm_pipe | — | — | — | — | — | — | — |
| `92f139a3...-C` | **psd_pipe** | psd_pipe | — | — | — | — | — | — | — |
| `026f3c37...-C` | **psp** | psp | — | — | — | — | — | — | — |
| `2cb4bf29...-C` | **psxstr** | psxstr | — | — | — | — | — | — | — |
| `3068c5a0...-C` | **pva** | pva | — | — | — | — | — | — | — |
| `2e74785c...-C` | **pvf** | pvf | — | — | — | — | — | — | — |
| `f1cea715...-C` | **qcp** | qcp | — | — | — | — | — | — | — |
| `21d01a06...-C` | **qdraw_pipe** | qdraw_pipe | — | — | — | — | — | — | — |
| `7334275e...-C` | **qoa** | qoa | — | — | — | — | — | — | — |
| `537f3521...-C` | **qoi_pipe** | qoi_pipe | — | — | — | — | — | — | — |
| `db824543...-C` | **rawvideo** | rawvideo | — | — | — | — | — | — | — |
| `475743ce...-C` | **rcwt** | rcwt | — | — | — | — | — | — | — |
| `05b808e0...-C` | **realtext** | realtext | — | — | — | — | — | — | — |
| `ee3f41d2...-C` | **redspark** | redspark | — | — | — | — | — | — | — |
| `a6aa315f...-C` | **rka** | rka | — | — | — | — | — | — | — |
| `8820a7ae...-C` | **rl2** | rl2 | — | — | — | — | — | — | — |
| `1eb7e7fe...-C` | **rm** | rm | — | — | — | — | — | — | — |
| `0a4a5837...-C` | **roq** | roq | — | — | — | — | — | — | — |
| `ab1a8013...-C` | **rpl** | rpl | — | — | — | — | — | — | — |
| `1523b500...-C` | **rsd** | rsd | — | — | — | — | — | — | — |
| `3353e35c...-C` | **rso** | rso | — | — | — | — | — | — | — |
| `8bcef317...-C` | **rtp** | rtp | — | — | — | — | — | — | — |
| `dcf2069e...-C` | **rtp_mpegts** | rtp_mpegts | — | — | — | — | — | — | — |
| `797aa974...-C` | **rtsp** | rtsp | — | — | — | — | — | — | — |
| `616a3783...-C` | **s16be** | s16be | — | — | — | — | — | — | — |
| `337ad944...-C` | **s16le** | s16le | — | — | — | — | — | — | — |
| `ec46128f...-C` | **s24be** | s24be | — | — | — | — | — | — | — |
| `b3116c5c...-C` | **s24le** | s24le | — | — | — | — | — | — | — |
| `be8fe302...-C` | **s32be** | s32be | — | — | — | — | — | — | — |
| `7d022f7e...-C` | **s32le** | s32le | — | — | — | — | — | — | — |
| `531cf635...-C` | **s337m** | s337m | — | — | — | — | — | — | — |
| `a882166a...-C` | **s8** | s8 | — | — | — | — | — | — | — |
| `d90b259c...-C` | **sami** | sami | — | — | — | — | — | — | — |
| `060dd15a...-C` | **sap** | sap | — | — | — | — | — | — | — |
| `187ed794...-C` | **sbc** | sbc | — | — | — | — | — | — | — |
| `96233e8d...-C` | **sbg** | sbg | — | — | — | — | — | — | — |
| `3ea72426...-C` | **scc** | scc | — | — | — | — | — | — | — |
| `e5ccd098...-C` | **scd** | scd | — | — | — | — | — | — | — |
| `fba1d08d...-C` | **sdns** | sdns | — | — | — | — | — | — | — |
| `da512b2f...-C` | **sdp** | sdp | — | — | — | — | — | — | — |
| `d3e3ee55...-C` | **sdr2** | sdr2 | — | — | — | — | — | — | — |
| `ed4f1900...-C` | **sds** | sds | — | — | — | — | — | — | — |
| `b6f95b58...-C` | **sdx** | sdx | — | — | — | — | — | — | — |
| `ac055043...-C` | **segment** | segment | — | — | — | — | — | — | — |
| `4ce6ba6e...-C` | **ser** | ser | — | — | — | — | — | — | — |
| `c3aa3b80...-C` | **sga** | sga | — | — | — | — | — | — | — |
| `da554093...-C` | **sgi_pipe** | sgi_pipe | — | — | — | — | — | — | — |
| `995f398c...-C` | **shn** | shn | — | — | — | — | — | — | — |
| `6c95549f...-C` | **siff** | siff | — | — | — | — | — | — | — |
| `5f65238e...-C` | **simbiosis_imx** | simbiosis_imx | — | — | — | — | — | — | — |
| `6f61e170...-C` | **sln** | sln | — | — | — | — | — | — | — |
| `39a54154...-C` | **smjpeg** | smjpeg | — | — | — | — | — | — | — |
| `f5828f43...-C` | **smk** | smk | — | — | — | — | — | — | — |
| `f43c145b...-C` | **smoothstreaming** | smoothstreaming | — | — | — | — | — | — | — |
| `d1d8d935...-C` | **smush** | smush | — | — | — | — | — | — | — |
| `9160f005...-C` | **sol** | sol | — | — | — | — | — | — | — |
| `1d736177...-C` | **sox** | sox | — | — | — | — | — | — | — |
| `8bbf425d...-C` | **spdif** | spdif | — | — | — | — | — | — | — |
| `823e4c9b...-C` | **spx** | spx | — | — | — | — | — | — | — |
| `2d9dd1b2...-C` | **srt** | srt | — | — | — | — | — | — | — |
| `c9d6c414...-C` | **stl** | stl | — | — | — | — | — | — | — |
| `7a4a44aa...-C` | **stream_segment,ssegment** | stream_segment,ssegment | — | — | — | — | — | — | — |
| `fba042dc...-C` | **streamhash** | streamhash | — | — | — | — | — | — | — |
| `9f050517...-C` | **subviewer** | subviewer | — | — | — | — | — | — | — |
| `415fc2b5...-C` | **subviewer1** | subviewer1 | — | — | — | — | — | — | — |
| `ab762315...-C` | **sunrast_pipe** | sunrast_pipe | — | — | — | — | — | — | — |
| `cec5a159...-C` | **sup** | sup | — | — | — | — | — | — | — |
| `deeb6e29...-C` | **svag** | svag | — | — | — | — | — | — | — |
| `d685525d...-C` | **svcd** | svcd | — | — | — | — | — | — | — |
| `84321957...-C` | **svg_pipe** | svg_pipe | — | — | — | — | — | — | — |
| `33b7109e...-C` | **svs** | svs | — | — | — | — | — | — | — |
| `b1c9f4aa...-C` | **swf** | swf | — | — | — | — | — | — | — |
| `983acf7f...-C` | **tak** | tak | — | — | — | — | — | — | — |
| `67fc34b3...-C` | **tedcaptions** | tedcaptions | — | — | — | — | — | — | — |
| `ea6aead1...-C` | **tee** | tee | — | — | — | — | — | — | — |
| `d8ef3601...-C` | **thp** | thp | — | — | — | — | — | — | — |
| `73a753d2...-C` | **tiertexseq** | tiertexseq | — | — | — | — | — | — | — |
| `320b80dd...-C` | **tiff_pipe** | tiff_pipe | — | — | — | — | — | — | — |
| `a39f2552...-C` | **tmv** | tmv | — | — | — | — | — | — | — |
| `68cbc40c...-C` | **truehd** | truehd | — | — | — | — | — | — | — |
| `85ad801b...-C` | **tta** | tta | — | — | — | — | — | — | — |
| `62d9b169...-C` | **ttml** | ttml | — | — | — | — | — | — | — |
| `2b929086...-C` | **tty** | tty | — | — | — | — | — | — | — |
| `d441ea77...-C` | **txd** | txd | — | — | — | — | — | — | — |
| `a8423078...-C` | **ty** | ty | — | — | — | — | — | — | — |
| `ffbfbf26...-C` | **u16be** | u16be | — | — | — | — | — | — | — |
| `afed4088...-C` | **u16le** | u16le | — | — | — | — | — | — | — |
| `4148d717...-C` | **u24be** | u24be | — | — | — | — | — | — | — |
| `11e0a5f1...-C` | **u24le** | u24le | — | — | — | — | — | — | — |
| `cb8afe1c...-C` | **u32be** | u32be | — | — | — | — | — | — | — |
| `cbf5aaf1...-C` | **u32le** | u32le | — | — | — | — | — | — | — |
| `0f45e7c5...-C` | **u8** | u8 | — | — | — | — | — | — | — |
| `000620bc...-C` | **uncodedframecrc** | uncodedframecrc | — | — | — | — | — | — | — |
| `76acb1d8...-C` | **usm** | usm | — | — | — | — | — | — | — |
| `893873d4...-C` | **v210** | v210 | — | — | — | — | — | — | — |
| `229b4a1c...-C` | **v210x** | v210x | — | — | — | — | — | — | — |
| `37c4b278...-C` | **vag** | vag | — | — | — | — | — | — | — |
| `3a2b25dc...-C` | **vbn_pipe** | vbn_pipe | — | — | — | — | — | — | — |
| `e2f43af1...-C` | **vc1** | vc1 | — | — | — | — | — | — | — |
| `002c6ea6...-C` | **vc1test** | vc1test | — | — | — | — | — | — | — |
| `74ee2b27...-C` | **vcd** | vcd | — | — | — | — | — | — | — |
| `648d0dc2...-C` | **vidc** | vidc | — | — | — | — | — | — | — |
| `75ffa0ee...-C` | **vividas** | vividas | — | — | — | — | — | — | — |
| `81475378...-C` | **vivo** | vivo | — | — | — | — | — | — | — |
| `c4fb7d10...-C` | **vmd** | vmd | — | — | — | — | — | — | — |
| `edcb37c8...-C` | **vob** | vob | — | — | — | — | — | — | — |
| `4e3c322a...-C` | **vobsub** | vobsub | — | — | — | — | — | — | — |
| `b49b9891...-C` | **voc** | voc | — | — | — | — | — | — | — |
| `ad6eff82...-C` | **vpk** | vpk | — | — | — | — | — | — | — |
| `4ad73c03...-C` | **vplayer** | vplayer | — | — | — | — | — | — | — |
| `1ebcccf3...-C` | **vqf** | vqf | — | — | — | — | — | — | — |
| `8067205d...-C` | **vvc** | vvc | — | — | — | — | — | — | — |
| `537ff079...-C` | **w64** | w64 | — | — | — | — | — | — | — |
| `a9626ea6...-C` | **wady** | wady | — | — | — | — | — | — | — |
| `71ed6c49...-C` | **wav** | wav | — | — | — | — | — | — | — |
| `186f2a54...-C` | **wavarc** | wavarc | — | — | — | — | — | — | — |
| `8d33fcbe...-C` | **wc3movie** | wc3movie | — | — | — | — | — | — | — |
| `795dcbf5...-C` | **webm** | webm | WebM | video/webm | — | — | — | N/A | WebM |
| `6e6d4cb9...-C` | **webm_chunk** | webm_chunk | — | — | — | — | — | — | — |
| `fcc871e3...-C` | **webm_dash_manifest** | webm_dash_manifest | — | — | — | — | — | — | — |
| `44d212be...-C` | **webp_pipe** | webp_pipe | — | — | — | — | — | — | — |
| `8ac80dbd...-C` | **webvtt** | webvtt | — | — | — | — | — | — | — |
| `4705a69f...-C` | **wsaud** | wsaud | — | — | — | — | — | — | — |
| `ac579e43...-C` | **wsd** | wsd | — | — | — | — | — | — | — |
| `846ae66a...-C` | **wsvqa** | wsvqa | — | — | — | — | — | — | — |
| `ccf121d1...-C` | **wtv** | wtv | — | — | — | — | — | — | — |
| `4ce30147...-C` | **wv** | wv | — | — | — | — | — | — | — |
| `ddd135b5...-C` | **wve** | wve | — | — | — | — | — | — | — |
| `10c4aa6b...-C` | **xa** | xa | — | — | — | — | — | — | — |
| `60885bc3...-C` | **xbin** | xbin | — | — | — | — | — | — | — |
| `0c46d931...-C` | **xbm_pipe** | xbm_pipe | — | — | — | — | — | — | — |
| `1cba27e5...-C` | **xmd** | xmd | — | — | — | — | — | — | — |
| `a46aa7da...-C` | **xmv** | xmv | — | — | — | — | — | — | — |
| `77f88520...-C` | **xpm_pipe** | xpm_pipe | — | — | — | — | — | — | — |
| `3053c113...-C` | **xvag** | xvag | — | — | — | — | — | — | — |
| `76f19650...-C` | **xwd_pipe** | xwd_pipe | — | — | — | — | — | — | — |
| `9fbd4432...-C` | **xwma** | xwma | — | — | — | — | — | — | — |
| `e2f128d9...-C` | **yop** | yop | — | — | — | — | — | — | — |
| `59675ad9...-C` | **yuv4mpegpipe** | yuv4mpegpipe | — | — | — | — | — | — | — |

### Video Codecs

| UUID (Type-Suffixed) | Canonical Name | ffprobe | libmagic | puremagic | pyfsig | binwalk | rawpy | Pillow | exiftool |
|---------------------|---------------|---------|----------|-----------|--------|---------|-------|--------|----------|
| `5646ca69...-V` | **alias_pix** | alias_pix | — | — | — | — | — | — | — |
| `3cf8e243...-V` | **amv** | amv | — | — | — | — | — | — | — |
| `575737c9...-V` | **apng** | apng | — | — | — | — | — | — | — |
| `99b1f2d0...-V` | **asv1** | asv1 | — | — | — | — | — | — | — |
| `c947275d...-V` | **asv2** | asv2 | — | — | — | — | — | — | — |
| `c69693cd...-V` | **av1** | av1 | ISO Media | video/mp4 | — | — | — | N/A | AV1 |
| `e3f55e0f...-V` | **avrp** | avrp | — | — | — | — | — | — | — |
| `7b206556...-V` | **avui** | avui | — | — | — | — | — | — | — |
| `0b299a0c...-V` | **bitpacked** | bitpacked | — | — | — | — | — | — | — |
| `2bc02020...-V` | **bmp** | bmp | — | — | — | — | — | — | — |
| `b648cd1e...-V` | **cfhd** | cfhd | — | — | — | — | — | — | — |
| `332063c0...-V` | **cinepak** | cinepak | — | — | — | — | — | — | — |
| `2b31543d...-V` | **cljr** | cljr | — | — | — | — | — | — | — |
| `71ee9d35...-V` | **dirac** | dirac | — | — | — | — | — | — | — |
| `d84fd63d...-V` | **dnxhd** | dnxhd | — | — | — | — | — | — | — |
| `d17eedba...-V` | **dpx** | dpx | — | — | — | — | — | — | — |
| `301bc50a...-V` | **dvvideo** | dvvideo | — | — | — | — | — | — | — |
| `7af4fa67...-V` | **dxv** | dxv | — | — | — | — | — | — | — |
| `a6a5d9fa...-V` | **exr** | exr | — | — | — | — | — | — | — |
| `6de418ad...-V` | **ffv1** | ffv1 | — | — | — | — | — | — | — |
| `4a58899f...-V` | **ffvhuff** | ffvhuff | — | — | — | — | — | — | — |
| `7edee68c...-V` | **fits** | fits | — | — | — | — | — | — | — |
| `6bfc16ef...-V` | **flashsv** | flashsv | — | — | — | — | — | — | — |
| `1ed7f29e...-V` | **flashsv2** | flashsv2 | — | — | — | — | — | — | — |
| `377b6c61...-V` | **flv1** | flv1 | — | — | — | — | — | — | — |
| `027f3fb3...-V` | **gif** | gif | GIF image data | image/gif | — | — | — | GIF | GIF |
| `3452bf5e...-V` | **h261** | h261 | — | — | — | — | — | — | — |
| `ba1d20a6...-V` | **h263** | h263 | — | — | — | — | — | — | — |
| `45843b06...-V` | **h263p** | h263p | — | — | — | — | — | — | — |
| `b2e62c4a...-V` | **h264** | h264 | MPEG v4 system | video/mp4 | — | — | — | N/A | AVC |
| `b00d4f7f...-V` | **hap** | hap | — | — | — | — | — | — | — |
| `1fa2d4ca...-V` | **hdr** | hdr | — | — | — | — | — | — | — |
| `faf4b553...-V` | **hevc** | hevc | ISO Media | video/mp4 | — | — | — | N/A | HEVC |
| `b36d076f...-V` | **huffyuv** | huffyuv | — | — | — | — | — | — | — |
| `d1349945...-V` | **jpeg2000** | jpeg2000 | — | — | — | — | — | — | — |
| `c5383a2e...-V` | **jpegls** | jpegls | — | — | — | — | — | — | — |
| `f27384fa...-V` | **jpegxl** | jpegxl | — | — | — | — | — | — | — |
| `1799f0dc...-V` | **jpegxl_anim** | jpegxl_anim | — | — | — | — | — | — | — |
| `b43b9c32...-V` | **magicyuv** | magicyuv | — | — | — | — | — | — | — |
| `082454e8...-V` | **mjpeg** | mjpeg | — | — | — | — | — | — | — |
| `b90ff05b...-V` | **mpeg1video** | mpeg1video | — | — | — | — | — | — | — |
| `260ba350...-V` | **mpeg2video** | mpeg2video | — | — | — | — | — | — | — |
| `61a6cea9...-V` | **mpeg4** | mpeg4 | — | — | — | — | — | — | — |
| `6ace59c7...-V` | **msmpeg4v2** | msmpeg4v2 | — | — | — | — | — | — | — |
| `10306bcb...-V` | **msmpeg4v3** | msmpeg4v3 | — | — | — | — | — | — | — |
| `64798a74...-V` | **msrle** | msrle | — | — | — | — | — | — | — |
| `df87246b...-V` | **msvideo1** | msvideo1 | — | — | — | — | — | — | — |
| `9be619e9...-V` | **pam** | pam | — | — | — | — | — | — | — |
| `d7466c05...-V` | **pbm** | pbm | — | — | — | — | — | — | — |
| `94e95463...-V` | **pcx** | pcx | — | — | — | — | — | — | — |
| `a0e42d70...-V` | **pfm** | pfm | — | — | — | — | — | — | — |
| `b195d3ac...-V` | **pgm** | pgm | — | — | — | — | — | — | — |
| `a9a8bd10...-V` | **pgmyuv** | pgmyuv | — | — | — | — | — | — | — |
| `4765ea09...-V` | **phm** | phm | — | — | — | — | — | — | — |
| `47d2f243...-V` | **png** | png | PNG image data | image/png | — | — | — | PNG | PNG |
| `390cbf23...-V` | **ppm** | ppm | — | — | — | — | — | — | — |
| `5199d417...-V` | **prores** | prores | — | — | — | — | — | — | — |
| `824fc9cc...-V` | **qoi** | qoi | — | — | — | — | — | — | — |
| `0f71871e...-V` | **qtrle** | qtrle | — | — | — | — | — | — | — |
| `cbc92ca3...-V` | **r10k** | r10k | — | — | — | — | — | — | — |
| `d104d523...-V` | **r210** | r210 | — | — | — | — | — | — | — |
| `296794c5...-V` | **rawvideo** | rawvideo | — | — | — | — | — | — | — |
| `eeba117d...-V` | **roq** | roq | — | — | — | — | — | — | — |
| `ad075e0c...-V` | **rpza** | rpza | — | — | — | — | — | — | — |
| `c2334986...-V` | **rv10** | rv10 | — | — | — | — | — | — | — |
| `a1526dc0...-V` | **rv20** | rv20 | — | — | — | — | — | — | — |
| `a2353c6c...-V` | **sgi** | sgi | — | — | — | — | — | — | — |
| `e3dba39b...-V` | **smc** | smc | — | — | — | — | — | — | — |
| `17b37aac...-V` | **snow** | snow | — | — | — | — | — | — | — |
| `9f649b3d...-V` | **speedhq** | speedhq | — | — | — | — | — | — | — |
| `33e8eb6b...-V` | **sunrast** | sunrast | — | — | — | — | — | — | — |
| `64dd14e7...-V` | **svq1** | svq1 | — | — | — | — | — | — | — |
| `451a8cb4...-V` | **targa** | targa | — | — | — | — | — | — | — |
| `8ea064ff...-V` | **theora** | theora | — | — | — | — | — | — | — |
| `9497b0d8...-V` | **tiff** | tiff | TIFF image data | image/tiff | — | — | — | TIFF | TIFF |
| `eec27b36...-V` | **utvideo** | utvideo | — | — | — | — | — | — | — |
| `a92f597a...-V` | **v210** | v210 | — | — | — | — | — | — | — |
| `37e0af28...-V` | **v308** | v308 | — | — | — | — | — | — | — |
| `a67e8f7a...-V` | **v408** | v408 | — | — | — | — | — | — | — |
| `48b301d7...-V` | **v410** | v410 | — | — | — | — | — | — | — |
| `9dcb9c5d...-V` | **vbn** | vbn | — | — | — | — | — | — | — |
| `36d3b462...-V` | **vnull** | vnull | — | — | — | — | — | — | — |
| `d91b7c22...-V` | **vp8** | vp8 | — | — | — | — | — | — | — |
| `4c9b19a7...-V` | **vp9** | vp9 | WebM | video/webm | — | — | — | N/A | VP9 |
| `abbe2402...-V` | **wbmp** | wbmp | — | — | — | — | — | — | — |
| `e9b99fb3...-V` | **webp** | webp | Web/P image | image/webp | — | — | — | WEBP | WebP |
| `fc1b84c9...-V` | **wmv1** | wmv1 | — | — | — | — | — | — | — |
| `7abdb54c...-V` | **wmv2** | wmv2 | — | — | — | — | — | — | — |
| `6085b98e...-V` | **wrapped_avframe** | wrapped_avframe | — | — | — | — | — | — | — |
| `a81dc308...-V` | **xbm** | xbm | — | — | — | — | — | — | — |
| `cf49a3a9...-V` | **xface** | xface | — | — | — | — | — | — | — |
| `cadf6061...-V` | **xwd** | xwd | — | — | — | — | — | — | — |
| `a80d5ded...-V` | **y41p** | y41p | — | — | — | — | — | — | — |
| `a24a39ba...-V` | **yuv4** | yuv4 | — | — | — | — | — | — | — |
| `febb6d8a...-V` | **zlib** | zlib | — | — | — | — | — | — | — |
| `b8be0007...-V` | **zmbv** | zmbv | — | — | — | — | — | — | — |

### Audio Codecs

| UUID (Type-Suffixed) | Canonical Name | ffprobe | libmagic | puremagic | pyfsig | binwalk | rawpy | Pillow | exiftool |
|---------------------|---------------|---------|----------|-----------|--------|---------|-------|--------|----------|
| `cee232ec...-A` | **aac** | aac | — | — | — | — | — | — | — |
| `8453c376...-A` | **ac3** | ac3 | — | — | — | — | — | — | — |
| `8501512e...-A` | **adpcm_adx** | adpcm_adx | — | — | — | — | — | — | — |
| `efc63935...-A` | **adpcm_argo** | adpcm_argo | — | — | — | — | — | — | — |
| `b92cdc7c...-A` | **adpcm_g722** | adpcm_g722 | — | — | — | — | — | — | — |
| `105ede72...-A` | **adpcm_g726** | adpcm_g726 | — | — | — | — | — | — | — |
| `2442f4df...-A` | **adpcm_g726le** | adpcm_g726le | — | — | — | — | — | — | — |
| `85043c57...-A` | **adpcm_ima_alp** | adpcm_ima_alp | — | — | — | — | — | — | — |
| `78504cba...-A` | **adpcm_ima_amv** | adpcm_ima_amv | — | — | — | — | — | — | — |
| `01ee1797...-A` | **adpcm_ima_apm** | adpcm_ima_apm | — | — | — | — | — | — | — |
| `a054c645...-A` | **adpcm_ima_qt** | adpcm_ima_qt | — | — | — | — | — | — | — |
| `6407eabd...-A` | **adpcm_ima_ssi** | adpcm_ima_ssi | — | — | — | — | — | — | — |
| `53a79661...-A` | **adpcm_ima_wav** | adpcm_ima_wav | — | — | — | — | — | — | — |
| `986c5b36...-A` | **adpcm_ima_ws** | adpcm_ima_ws | — | — | — | — | — | — | — |
| `9bffd6b5...-A` | **adpcm_ms** | adpcm_ms | — | — | — | — | — | — | — |
| `2c731eaf...-A` | **adpcm_swf** | adpcm_swf | — | — | — | — | — | — | — |
| `532db01b...-A` | **adpcm_yamaha** | adpcm_yamaha | — | — | — | — | — | — | — |
| `98638ebf...-A` | **alac** | alac | — | — | — | — | — | — | — |
| `1df28a87...-A` | **amr_nb** | amr_nb | — | — | — | — | — | — | — |
| `542b1274...-A` | **anull** | anull | — | — | — | — | — | — | — |
| `4c1f222f...-A` | **aptx** | aptx | — | — | — | — | — | — | — |
| `d7588046...-A` | **aptx_hd** | aptx_hd | — | — | — | — | — | — | — |
| `79b1fd9b...-A` | **comfortnoise** | comfortnoise | — | — | — | — | — | — | — |
| `10899c05...-A` | **dfpwm** | dfpwm | — | — | — | — | — | — | — |
| `b8369c87...-A` | **dts** | dts | — | — | — | — | — | — | — |
| `21261078...-A` | **eac3** | eac3 | — | — | — | — | — | — | — |
| `1fe79ce5...-A` | **flac** | flac | — | — | — | — | — | — | — |
| `9f6f0ffc...-A` | **g723_1** | g723_1 | — | — | — | — | — | — | — |
| `72701c47...-A` | **ilbc** | ilbc | — | — | — | — | — | — | — |
| `11c31109...-A` | **mlp** | mlp | — | — | — | — | — | — | — |
| `3dd82777...-A` | **mp2** | mp2 | — | — | — | — | — | — | — |
| `9da4abe5...-A` | **mp3** | mp3 | — | — | — | — | — | — | — |
| `006b937d...-A` | **nellymoser** | nellymoser | — | — | — | — | — | — | — |
| `8faa0976...-A` | **opus** | opus | — | — | — | — | — | — | — |
| `a79b9884...-A` | **pcm_alaw** | pcm_alaw | — | — | — | — | — | — | — |
| `7acfc416...-A` | **pcm_bluray** | pcm_bluray | — | — | — | — | — | — | — |
| `3535a1af...-A` | **pcm_dvd** | pcm_dvd | — | — | — | — | — | — | — |
| `4cbb5323...-A` | **pcm_f32be** | pcm_f32be | — | — | — | — | — | — | — |
| `3138fb08...-A` | **pcm_f32le** | pcm_f32le | — | — | — | — | — | — | — |
| `7ba4281a...-A` | **pcm_f64be** | pcm_f64be | — | — | — | — | — | — | — |
| `b5fb6bc9...-A` | **pcm_f64le** | pcm_f64le | — | — | — | — | — | — | — |
| `e812c6d9...-A` | **pcm_mulaw** | pcm_mulaw | — | — | — | — | — | — | — |
| `6514e33f...-A` | **pcm_s16be** | pcm_s16be | — | — | — | — | — | — | — |
| `17a6250f...-A` | **pcm_s16be_planar** | pcm_s16be_planar | — | — | — | — | — | — | — |
| `b925925b...-A` | **pcm_s16le** | pcm_s16le | — | — | — | — | — | — | — |
| `6e405ebc...-A` | **pcm_s16le_planar** | pcm_s16le_planar | — | — | — | — | — | — | — |
| `8db792ed...-A` | **pcm_s24be** | pcm_s24be | — | — | — | — | — | — | — |
| `cbff247d...-A` | **pcm_s24daud** | pcm_s24daud | — | — | — | — | — | — | — |
| `76f5a80c...-A` | **pcm_s24le** | pcm_s24le | — | — | — | — | — | — | — |
| `6fde9a3a...-A` | **pcm_s24le_planar** | pcm_s24le_planar | — | — | — | — | — | — | — |
| `730bf178...-A` | **pcm_s32be** | pcm_s32be | — | — | — | — | — | — | — |
| `9f7149f5...-A` | **pcm_s32le** | pcm_s32le | — | — | — | — | — | — | — |
| `76376c2b...-A` | **pcm_s32le_planar** | pcm_s32le_planar | — | — | — | — | — | — | — |
| `4cb8d100...-A` | **pcm_s64be** | pcm_s64be | — | — | — | — | — | — | — |
| `d40c5eb6...-A` | **pcm_s64le** | pcm_s64le | — | — | — | — | — | — | — |
| `663e1bd7...-A` | **pcm_s8** | pcm_s8 | — | — | — | — | — | — | — |
| `4b015a86...-A` | **pcm_s8_planar** | pcm_s8_planar | — | — | — | — | — | — | — |
| `b7a37796...-A` | **pcm_u16be** | pcm_u16be | — | — | — | — | — | — | — |
| `1f3cf0d2...-A` | **pcm_u16le** | pcm_u16le | — | — | — | — | — | — | — |
| `e0e15a8f...-A` | **pcm_u24be** | pcm_u24be | — | — | — | — | — | — | — |
| `4c309438...-A` | **pcm_u24le** | pcm_u24le | — | — | — | — | — | — | — |
| `9afd411f...-A` | **pcm_u32be** | pcm_u32be | — | — | — | — | — | — | — |
| `3103cb65...-A` | **pcm_u32le** | pcm_u32le | — | — | — | — | — | — | — |
| `172ae5c5...-A` | **pcm_u8** | pcm_u8 | — | — | — | — | — | — | — |
| `6a6cc0a6...-A` | **pcm_vidc** | pcm_vidc | — | — | — | — | — | — | — |
| `688c6d5a...-A` | **ra_144** | ra_144 | — | — | — | — | — | — | — |
| `c05d3129...-A` | **roq_dpcm** | roq_dpcm | — | — | — | — | — | — | — |
| `043a0079...-A` | **s302m** | s302m | — | — | — | — | — | — | — |
| `e7f84648...-A` | **sbc** | sbc | — | — | — | — | — | — | — |
| `e5d98d48...-A` | **speex** | speex | — | — | — | — | — | — | — |
| `26282d63...-A` | **truehd** | truehd | — | — | — | — | — | — | — |
| `9c62fa8b...-A` | **tta** | tta | — | — | — | — | — | — | — |
| `acf1a687...-A` | **vorbis** | vorbis | — | — | — | — | — | — | — |
| `888a6208...-A` | **wavpack** | wavpack | — | — | — | — | — | — | — |
| `7ffe2fb7...-A` | **wmav1** | wmav1 | — | — | — | — | — | — | — |
| `5ee4140d...-A` | **wmav2** | wmav2 | — | — | — | — | — | — | — |

### Image Formats

| UUID (Type-Suffixed) | Canonical Name | ffprobe | libmagic | puremagic | pyfsig | binwalk | rawpy | Pillow | exiftool |
|---------------------|---------------|---------|----------|-----------|--------|---------|-------|--------|----------|
| `169ebedc...-I` | **avif** | avif | ISO Media | image/avif | — | — | — | AVIF | AVIF |
| `808b7568...-I` | **gif** | gif | GIF image data | image/gif | — | — | — | GIF | GIF |
| `768db60f...-I` | **heif** | heif | ISO Media | image/heif | — | — | — | HEIF | HEIF |
| `c416405f...-I` | **jxl** | jxl | JPEG XL codestream | image/jxl | — | — | — | N/A | JXL |
| `002b5a9f...-I` | **webp** | webp | Web/P image | image/webp | — | — | — | WEBP | WebP |

### Camera RAW Formats

| UUID (Type-Suffixed) | Canonical Name | ffprobe | libmagic | puremagic | pyfsig | binwalk | rawpy | Pillow | exiftool |
|---------------------|---------------|---------|----------|-----------|--------|---------|-------|--------|----------|
| `facc476b...-R` | **arw** | N/A | Sony ARW RAW | image/x-sony-arw | — | — | ARW | N/A | ARW |
| `ac126046...-R` | **cr2** | N/A | Canon CR2 RAW | image/x-canon-cr2 | — | — | CR2 | N/A | CR2 |
| `a829ec18...-R` | **cr3** | N/A | Canon CR3 | image/x-canon-cr3 | — | — | CR3 | N/A | CR3 |
| `ae6404c9...-R` | **dng** | N/A | Adobe DNG | image/x-adobe-dng | — | — | DNG | N/A | DNG |
| `16e292ec...-R` | **nef** | N/A | Nikon NEF RAW | image/x-nikon-nef | — | — | NEF | N/A | NEF |
| `b2f15c88...-R` | **orf** | N/A | Olympus ORF RAW | image/x-olympus-orf | — | — | ORF | N/A | ORF |
| `8e2ac93c...-R` | **pef** | pef | — | — | — | — | — | — | — |
| `a5e9f1bb...-R` | **r3d** | r3d | — | — | — | — | — | — | — |
| `a9997994...-R` | **raf** | N/A | Fujifilm RAF | image/x-fuji-raf | — | — | RAF | N/A | RAF |
| `c3fbb54e...-R` | **rw2** | N/A | Panasonic RW2 RAW | image/x-panasonic-rw2 | — | — | RW2 | N/A | RW2 |
| `0283bda1...-R` | **srw** | srw | — | — | — | — | — | — | — |

### Pixel Formats

| UUID (Type-Suffixed) | Canonical Name | ffprobe | libmagic | puremagic | pyfsig | binwalk | rawpy | Pillow | exiftool |
|---------------------|---------------|---------|----------|-----------|--------|---------|-------|--------|----------|
| `f95cf84d...-P` | **0bgr** | 0bgr | — | — | — | — | — | — | — |
| `85ea9e96...-P` | **0rgb** | 0rgb | — | — | — | — | — | — | — |
| `4017c4f1...-P` | **abgr** | abgr | — | — | — | — | — | — | — |
| `d89888d0...-P` | **amf** | amf | — | — | — | — | — | — | — |
| `983e0b8f...-P` | **argb** | argb | — | — | — | — | — | — | — |
| `9daf70d6...-P` | **ayuv** | ayuv | — | — | — | — | — | — | — |
| `a66439ef...-P` | **ayuv64be** | ayuv64be | — | — | — | — | — | — | — |
| `033ea2b2...-P` | **ayuv64le** | ayuv64le | — | — | — | — | — | — | — |
| `3882a9e2...-P` | **bayer_bggr16be** | bayer_bggr16be | — | — | — | — | — | — | — |
| `d2b8c2cb...-P` | **bayer_bggr16le** | bayer_bggr16le | — | — | — | — | — | — | — |
| `e53943fa...-P` | **bayer_bggr8** | bayer_bggr8 | — | — | — | — | — | — | — |
| `282c893c...-P` | **bayer_gbrg16be** | bayer_gbrg16be | — | — | — | — | — | — | — |
| `65cd3f75...-P` | **bayer_gbrg16le** | bayer_gbrg16le | — | — | — | — | — | — | — |
| `774bb201...-P` | **bayer_gbrg8** | bayer_gbrg8 | — | — | — | — | — | — | — |
| `af428b58...-P` | **bayer_grbg16be** | bayer_grbg16be | — | — | — | — | — | — | — |
| `2a4b6929...-P` | **bayer_grbg16le** | bayer_grbg16le | — | — | — | — | — | — | — |
| `abc405e2...-P` | **bayer_grbg8** | bayer_grbg8 | — | — | — | — | — | — | — |
| `1b6022ce...-P` | **bayer_rggb16be** | bayer_rggb16be | — | — | — | — | — | — | — |
| `8e68b204...-P` | **bayer_rggb16le** | bayer_rggb16le | — | — | — | — | — | — | — |
| `af6879f7...-P` | **bayer_rggb8** | bayer_rggb8 | — | — | — | — | — | — | — |
| `8c2b05ef...-P` | **bgr0** | bgr0 | — | — | — | — | — | — | — |
| `f0cf2e5f...-P` | **bgr24** | bgr24 | — | — | — | — | — | — | — |
| `1c02a525...-P` | **bgr4** | bgr4 | — | — | — | — | — | — | — |
| `5f615d34...-P` | **bgr444be** | bgr444be | — | — | — | — | — | — | — |
| `bd842e39...-P` | **bgr444le** | bgr444le | — | — | — | — | — | — | — |
| `a3280f96...-P` | **bgr48be** | bgr48be | — | — | — | — | — | — | — |
| `651b4a53...-P` | **bgr48le** | bgr48le | — | — | — | — | — | — | — |
| `64a9a1e4...-P` | **bgr4_byte** | bgr4_byte | — | — | — | — | — | — | — |
| `57ce6f2f...-P` | **bgr555be** | bgr555be | — | — | — | — | — | — | — |
| `f61bf438...-P` | **bgr555le** | bgr555le | — | — | — | — | — | — | — |
| `0f2d1686...-P` | **bgr565be** | bgr565be | — | — | — | — | — | — | — |
| `b65b8eac...-P` | **bgr565le** | bgr565le | — | — | — | — | — | — | — |
| `8140c928...-P` | **bgr8** | bgr8 | — | — | — | — | — | — | — |
| `08fc966a...-P` | **bgra** | bgra | — | — | — | — | — | — | — |
| `bf383723...-P` | **bgra64be** | bgra64be | — | — | — | — | — | — | — |
| `696dd3be...-P` | **bgra64le** | bgra64le | — | — | — | — | — | — | — |
| `5adf8fde...-P` | **cuda** | cuda | — | — | — | — | — | — | — |
| `514ee48c...-P` | **d3d11** | d3d11 | — | — | — | — | — | — | — |
| `8a96c9d1...-P` | **d3d11va_vld** | d3d11va_vld | — | — | — | — | — | — | — |
| `29f4bc1c...-P` | **d3d12** | d3d12 | — | — | — | — | — | — | — |
| `6ed63d45...-P` | **drm_prime** | drm_prime | — | — | — | — | — | — | — |
| `95902d5b...-P` | **dxva2_vld** | dxva2_vld | — | — | — | — | — | — | — |
| `80d21716...-P` | **gbrap** | gbrap | — | — | — | — | — | — | — |
| `67c1f16b...-P` | **gbrap10be** | gbrap10be | — | — | — | — | — | — | — |
| `fc708c80...-P` | **gbrap10le** | gbrap10le | — | — | — | — | — | — | — |
| `6b3c5f30...-P` | **gbrap12be** | gbrap12be | — | — | — | — | — | — | — |
| `0517a731...-P` | **gbrap12le** | gbrap12le | — | — | — | — | — | — | — |
| `ee15ef3b...-P` | **gbrap14be** | gbrap14be | — | — | — | — | — | — | — |
| `2ee14192...-P` | **gbrap14le** | gbrap14le | — | — | — | — | — | — | — |
| `2c466cab...-P` | **gbrap16be** | gbrap16be | — | — | — | — | — | — | — |
| `39a67a31...-P` | **gbrap16le** | gbrap16le | — | — | — | — | — | — | — |
| `317d613d...-P` | **gbrap32be** | gbrap32be | — | — | — | — | — | — | — |
| `906bc147...-P` | **gbrap32le** | gbrap32le | — | — | — | — | — | — | — |
| `b67bfaf9...-P` | **gbrapf16be** | gbrapf16be | — | — | — | — | — | — | — |
| `8f6ff09c...-P` | **gbrapf16le** | gbrapf16le | — | — | — | — | — | — | — |
| `0bf56bda...-P` | **gbrapf32be** | gbrapf32be | — | — | — | — | — | — | — |
| `4ef3a109...-P` | **gbrapf32le** | gbrapf32le | — | — | — | — | — | — | — |
| `7e608415...-P` | **gbrp** | gbrp | — | — | — | — | — | — | — |
| `c25511c2...-P` | **gbrp10be** | gbrp10be | — | — | — | — | — | — | — |
| `978bf145...-P` | **gbrp10le** | gbrp10le | — | — | — | — | — | — | — |
| `80169ad7...-P` | **gbrp10msbbe** | gbrp10msbbe | — | — | — | — | — | — | — |
| `a09df4d9...-P` | **gbrp10msble** | gbrp10msble | — | — | — | — | — | — | — |
| `139e40eb...-P` | **gbrp12be** | gbrp12be | — | — | — | — | — | — | — |
| `8df8d81f...-P` | **gbrp12le** | gbrp12le | — | — | — | — | — | — | — |
| `c09bbe8b...-P` | **gbrp12msbbe** | gbrp12msbbe | — | — | — | — | — | — | — |
| `ce4d21d8...-P` | **gbrp12msble** | gbrp12msble | — | — | — | — | — | — | — |
| `afee8954...-P` | **gbrp14be** | gbrp14be | — | — | — | — | — | — | — |
| `63b57793...-P` | **gbrp14le** | gbrp14le | — | — | — | — | — | — | — |
| `ba916d9f...-P` | **gbrp16be** | gbrp16be | — | — | — | — | — | — | — |
| `19f5877c...-P` | **gbrp16le** | gbrp16le | — | — | — | — | — | — | — |
| `647b0f34...-P` | **gbrp9be** | gbrp9be | — | — | — | — | — | — | — |
| `a2fec621...-P` | **gbrp9le** | gbrp9le | — | — | — | — | — | — | — |
| `88f6aa64...-P` | **gbrpf16be** | gbrpf16be | — | — | — | — | — | — | — |
| `8cd0add7...-P` | **gbrpf16le** | gbrpf16le | — | — | — | — | — | — | — |
| `413bf505...-P` | **gbrpf32be** | gbrpf32be | — | — | — | — | — | — | — |
| `7e2fd5b6...-P` | **gbrpf32le** | gbrpf32le | — | — | — | — | — | — | — |
| `0d724a1d...-P` | **gray** | gray | — | — | — | — | — | — | — |
| `67682a41...-P` | **gray10be** | gray10be | — | — | — | — | — | — | — |
| `05a0295c...-P` | **gray10le** | gray10le | — | — | — | — | — | — | — |
| `bcd816e4...-P` | **gray12be** | gray12be | — | — | — | — | — | — | — |
| `5b31a2e9...-P` | **gray12le** | gray12le | — | — | — | — | — | — | — |
| `04985628...-P` | **gray14be** | gray14be | — | — | — | — | — | — | — |
| `94cb6824...-P` | **gray14le** | gray14le | — | — | — | — | — | — | — |
| `59742286...-P` | **gray16be** | gray16be | — | — | — | — | — | — | — |
| `f68ed970...-P` | **gray16le** | gray16le | — | — | — | — | — | — | — |
| `15f16d67...-P` | **gray32be** | gray32be | — | — | — | — | — | — | — |
| `1d23e8b2...-P` | **gray32le** | gray32le | — | — | — | — | — | — | — |
| `86d34a18...-P` | **gray9be** | gray9be | — | — | — | — | — | — | — |
| `f9f1b4ab...-P` | **gray9le** | gray9le | — | — | — | — | — | — | — |
| `0a55d4ea...-P` | **grayf16be** | grayf16be | — | — | — | — | — | — | — |
| `5b825b0d...-P` | **grayf16le** | grayf16le | — | — | — | — | — | — | — |
| `e8d71899...-P` | **grayf32be** | grayf32be | — | — | — | — | — | — | — |
| `9de73919...-P` | **grayf32le** | grayf32le | — | — | — | — | — | — | — |
| `eb3af5aa...-P` | **mediacodec** | mediacodec | — | — | — | — | — | — | — |
| `fcc233c0...-P` | **mmal** | mmal | — | — | — | — | — | — | — |
| `6e6faf58...-P` | **monob** | monob | — | — | — | — | — | — | — |
| `44645ee7...-P` | **monow** | monow | — | — | — | — | — | — | — |
| `c9f224a7...-P` | **nv12** | nv12 | — | — | — | — | — | — | — |
| `a5bfb076...-P` | **nv16** | nv16 | — | — | — | — | — | — | — |
| `5414b907...-P` | **nv20be** | nv20be | — | — | — | — | — | — | — |
| `cf231a94...-P` | **nv20le** | nv20le | — | — | — | — | — | — | — |
| `0ad88034...-P` | **nv21** | nv21 | — | — | — | — | — | — | — |
| `1a090ef5...-P` | **nv24** | nv24 | — | — | — | — | — | — | — |
| `5bfe0e9c...-P` | **nv42** | nv42 | — | — | — | — | — | — | — |
| `64440173...-P` | **ohcodec** | ohcodec | — | — | — | — | — | — | — |
| `a781ae6b...-P` | **opencl** | opencl | — | — | — | — | — | — | — |
| `3f7256ca...-P` | **p010be** | p010be | — | — | — | — | — | — | — |
| `42a6e6a3...-P` | **p010le** | p010le | — | — | — | — | — | — | — |
| `2193eb19...-P` | **p012be** | p012be | — | — | — | — | — | — | — |
| `36546a9d...-P` | **p012le** | p012le | — | — | — | — | — | — | — |
| `60c9d714...-P` | **p016be** | p016be | — | — | — | — | — | — | — |
| `3a03e0e1...-P` | **p016le** | p016le | — | — | — | — | — | — | — |
| `93389c17...-P` | **p210be** | p210be | — | — | — | — | — | — | — |
| `4e2ef0a1...-P` | **p210le** | p210le | — | — | — | — | — | — | — |
| `7ff921ea...-P` | **p212be** | p212be | — | — | — | — | — | — | — |
| `0757d257...-P` | **p212le** | p212le | — | — | — | — | — | — | — |
| `af3f54a1...-P` | **p216be** | p216be | — | — | — | — | — | — | — |
| `7f615899...-P` | **p216le** | p216le | — | — | — | — | — | — | — |
| `9107adf9...-P` | **p410be** | p410be | — | — | — | — | — | — | — |
| `2ea29ab7...-P` | **p410le** | p410le | — | — | — | — | — | — | — |
| `cc966980...-P` | **p412be** | p412be | — | — | — | — | — | — | — |
| `01b38f2b...-P` | **p412le** | p412le | — | — | — | — | — | — | — |
| `2a991239...-P` | **p416be** | p416be | — | — | — | — | — | — | — |
| `35a845c3...-P` | **p416le** | p416le | — | — | — | — | — | — | — |
| `3f8e02e4...-P` | **pal8** | pal8 | — | — | — | — | — | — | — |
| `10ad569a...-P` | **qsv** | qsv | — | — | — | — | — | — | — |
| `313958ff...-P` | **rgb0** | rgb0 | — | — | — | — | — | — | — |
| `712d8952...-P` | **rgb24** | rgb24 | — | — | — | — | — | — | — |
| `428e2a94...-P` | **rgb4** | rgb4 | — | — | — | — | — | — | — |
| `58057add...-P` | **rgb444be** | rgb444be | — | — | — | — | — | — | — |
| `a80db3b3...-P` | **rgb444le** | rgb444le | — | — | — | — | — | — | — |
| `2667c2b6...-P` | **rgb48be** | rgb48be | — | — | — | — | — | — | — |
| `f1c75b25...-P` | **rgb48le** | rgb48le | — | — | — | — | — | — | — |
| `7212e45f...-P` | **rgb4_byte** | rgb4_byte | — | — | — | — | — | — | — |
| `dd4c2ca8...-P` | **rgb555be** | rgb555be | — | — | — | — | — | — | — |
| `1e2068af...-P` | **rgb555le** | rgb555le | — | — | — | — | — | — | — |
| `6826a7ac...-P` | **rgb565be** | rgb565be | — | — | — | — | — | — | — |
| `eee93027...-P` | **rgb565le** | rgb565le | — | — | — | — | — | — | — |
| `e95a1704...-P` | **rgb8** | rgb8 | — | — | — | — | — | — | — |
| `016c28c8...-P` | **rgb96be** | rgb96be | — | — | — | — | — | — | — |
| `eaabbf4b...-P` | **rgb96le** | rgb96le | — | — | — | — | — | — | — |
| `111373e7...-P` | **rgba** | rgba | — | — | — | — | — | — | — |
| `16d4df13...-P` | **rgba128be** | rgba128be | — | — | — | — | — | — | — |
| `66d16e36...-P` | **rgba128le** | rgba128le | — | — | — | — | — | — | — |
| `c7cbd325...-P` | **rgba64be** | rgba64be | — | — | — | — | — | — | — |
| `3efc303d...-P` | **rgba64le** | rgba64le | — | — | — | — | — | — | — |
| `c09bfca7...-P` | **rgbaf16be** | rgbaf16be | — | — | — | — | — | — | — |
| `ec7bd932...-P` | **rgbaf16le** | rgbaf16le | — | — | — | — | — | — | — |
| `d7d25682...-P` | **rgbaf32be** | rgbaf32be | — | — | — | — | — | — | — |
| `fbb26650...-P` | **rgbaf32le** | rgbaf32le | — | — | — | — | — | — | — |
| `108f4e73...-P` | **rgbf16be** | rgbf16be | — | — | — | — | — | — | — |
| `25c958c0...-P` | **rgbf16le** | rgbf16le | — | — | — | — | — | — | — |
| `6a12dded...-P` | **rgbf32be** | rgbf32be | — | — | — | — | — | — | — |
| `9cc28f00...-P` | **rgbf32le** | rgbf32le | — | — | — | — | — | — | — |
| `f24e3288...-P` | **uyva** | uyva | — | — | — | — | — | — | — |
| `18867a22...-P` | **uyvy422** | uyvy422 | — | — | — | — | — | — | — |
| `85aff510...-P` | **uyyvyy411** | uyyvyy411 | — | — | — | — | — | — | — |
| `54d60651...-P` | **v30xbe** | v30xbe | — | — | — | — | — | — | — |
| `28e1848e...-P` | **v30xle** | v30xle | — | — | — | — | — | — | — |
| `473b09dd...-P` | **vaapi** | vaapi | — | — | — | — | — | — | — |
| `0b6ade1f...-P` | **vdpau** | vdpau | — | — | — | — | — | — | — |
| `e87ba2f5...-P` | **videotoolbox_vld** | videotoolbox_vld | — | — | — | — | — | — | — |
| `01c0be8f...-P` | **vulkan** | vulkan | — | — | — | — | — | — | — |
| `cfda7103...-P` | **vuya** | vuya | — | — | — | — | — | — | — |
| `9516bf72...-P` | **vuyx** | vuyx | — | — | — | — | — | — | — |
| `497e1861...-P` | **vyu444** | vyu444 | — | — | — | — | — | — | — |
| `0c60f06e...-P` | **x2bgr10be** | x2bgr10be | — | — | — | — | — | — | — |
| `cc2e96bf...-P` | **x2bgr10le** | x2bgr10le | — | — | — | — | — | — | — |
| `d57db321...-P` | **x2rgb10be** | x2rgb10be | — | — | — | — | — | — | — |
| `3fd69399...-P` | **x2rgb10le** | x2rgb10le | — | — | — | — | — | — | — |
| `e1ceff4a...-P` | **xv30be** | xv30be | — | — | — | — | — | — | — |
| `2fc7c0ab...-P` | **xv30le** | xv30le | — | — | — | — | — | — | — |
| `5ee9cf36...-P` | **xv36be** | xv36be | — | — | — | — | — | — | — |
| `111b0148...-P` | **xv36le** | xv36le | — | — | — | — | — | — | — |
| `5469dee1...-P` | **xv48be** | xv48be | — | — | — | — | — | — | — |
| `a496f172...-P` | **xv48le** | xv48le | — | — | — | — | — | — | — |
| `5ef2d866...-P` | **xyz12be** | xyz12be | — | — | — | — | — | — | — |
| `a0a11385...-P` | **xyz12le** | xyz12le | — | — | — | — | — | — | — |
| `4055f9d9...-P` | **y210be** | y210be | — | — | — | — | — | — | — |
| `b4d24256...-P` | **y210le** | y210le | — | — | — | — | — | — | — |
| `b9a72358...-P` | **y212be** | y212be | — | — | — | — | — | — | — |
| `e9497060...-P` | **y212le** | y212le | — | — | — | — | — | — | — |
| `5f651508...-P` | **y216be** | y216be | — | — | — | — | — | — | — |
| `1e8e52f5...-P` | **y216le** | y216le | — | — | — | — | — | — | — |
| `d3abdf2c...-P` | **ya16be** | ya16be | — | — | — | — | — | — | — |
| `9794358f...-P` | **ya16le** | ya16le | — | — | — | — | — | — | — |
| `bae63827...-P` | **ya8** | ya8 | — | — | — | — | — | — | — |
| `28f0518b...-P` | **yaf16be** | yaf16be | — | — | — | — | — | — | — |
| `55ba54ad...-P` | **yaf16le** | yaf16le | — | — | — | — | — | — | — |
| `84d0630e...-P` | **yaf32be** | yaf32be | — | — | — | — | — | — | — |
| `728bc5fb...-P` | **yaf32le** | yaf32le | — | — | — | — | — | — | — |
| `d2958ab9...-P` | **yuv410p** | yuv410p | — | — | — | — | — | — | — |
| `6cfda5d5...-P` | **yuv411p** | yuv411p | — | — | — | — | — | — | — |
| `7c724e5b...-P` | **yuv420p** | yuv420p | — | — | — | — | — | — | — |
| `989a5664...-P` | **yuv420p10be** | yuv420p10be | — | — | — | — | — | — | — |
| `d269b27e...-P` | **yuv420p10le** | yuv420p10le | — | — | — | — | — | — | — |
| `8833f09e...-P` | **yuv420p12be** | yuv420p12be | — | — | — | — | — | — | — |
| `9348ee7c...-P` | **yuv420p12le** | yuv420p12le | — | — | — | — | — | — | — |
| `a6cdc23f...-P` | **yuv420p14be** | yuv420p14be | — | — | — | — | — | — | — |
| `50dd2b44...-P` | **yuv420p14le** | yuv420p14le | — | — | — | — | — | — | — |
| `60cef4dd...-P` | **yuv420p16be** | yuv420p16be | — | — | — | — | — | — | — |
| `869975ea...-P` | **yuv420p16le** | yuv420p16le | — | — | — | — | — | — | — |
| `5571e9c3...-P` | **yuv420p9be** | yuv420p9be | — | — | — | — | — | — | — |
| `4565bb5f...-P` | **yuv420p9le** | yuv420p9le | — | — | — | — | — | — | — |
| `ae166841...-P` | **yuv422p** | yuv422p | — | — | — | — | — | — | — |
| `3f604d42...-P` | **yuv422p10be** | yuv422p10be | — | — | — | — | — | — | — |
| `4c74843e...-P` | **yuv422p10le** | yuv422p10le | — | — | — | — | — | — | — |
| `d1baabae...-P` | **yuv422p12be** | yuv422p12be | — | — | — | — | — | — | — |
| `3f78a926...-P` | **yuv422p12le** | yuv422p12le | — | — | — | — | — | — | — |
| `709ddd37...-P` | **yuv422p14be** | yuv422p14be | — | — | — | — | — | — | — |
| `bf09ac73...-P` | **yuv422p14le** | yuv422p14le | — | — | — | — | — | — | — |
| `3cc4b45e...-P` | **yuv422p16be** | yuv422p16be | — | — | — | — | — | — | — |
| `c1056fd9...-P` | **yuv422p16le** | yuv422p16le | — | — | — | — | — | — | — |
| `3ce6f699...-P` | **yuv422p9be** | yuv422p9be | — | — | — | — | — | — | — |
| `c4bd15bf...-P` | **yuv422p9le** | yuv422p9le | — | — | — | — | — | — | — |
| `cf1e3bb3...-P` | **yuv440p** | yuv440p | — | — | — | — | — | — | — |
| `e727c9dc...-P` | **yuv440p10be** | yuv440p10be | — | — | — | — | — | — | — |
| `0564b7f6...-P` | **yuv440p10le** | yuv440p10le | — | — | — | — | — | — | — |
| `7ab97f08...-P` | **yuv440p12be** | yuv440p12be | — | — | — | — | — | — | — |
| `d5e8adbc...-P` | **yuv440p12le** | yuv440p12le | — | — | — | — | — | — | — |
| `6698c78c...-P` | **yuv444p** | yuv444p | — | — | — | — | — | — | — |
| `6277bad2...-P` | **yuv444p10be** | yuv444p10be | — | — | — | — | — | — | — |
| `5acae7b9...-P` | **yuv444p10le** | yuv444p10le | — | — | — | — | — | — | — |
| `992881d4...-P` | **yuv444p10msbbe** | yuv444p10msbbe | — | — | — | — | — | — | — |
| `4d0eeeff...-P` | **yuv444p10msble** | yuv444p10msble | — | — | — | — | — | — | — |
| `665f2d43...-P` | **yuv444p12be** | yuv444p12be | — | — | — | — | — | — | — |
| `af039f23...-P` | **yuv444p12le** | yuv444p12le | — | — | — | — | — | — | — |
| `1379093d...-P` | **yuv444p12msbbe** | yuv444p12msbbe | — | — | — | — | — | — | — |
| `d6f1afde...-P` | **yuv444p12msble** | yuv444p12msble | — | — | — | — | — | — | — |
| `cf177923...-P` | **yuv444p14be** | yuv444p14be | — | — | — | — | — | — | — |
| `b17375d8...-P` | **yuv444p14le** | yuv444p14le | — | — | — | — | — | — | — |
| `98492ffc...-P` | **yuv444p16be** | yuv444p16be | — | — | — | — | — | — | — |
| `971ac667...-P` | **yuv444p16le** | yuv444p16le | — | — | — | — | — | — | — |
| `093552a5...-P` | **yuv444p9be** | yuv444p9be | — | — | — | — | — | — | — |
| `d84e76a0...-P` | **yuv444p9le** | yuv444p9le | — | — | — | — | — | — | — |
| `6ed1797b...-P` | **yuva420p** | yuva420p | — | — | — | — | — | — | — |
| `dca7b036...-P` | **yuva420p10be** | yuva420p10be | — | — | — | — | — | — | — |
| `5b217950...-P` | **yuva420p10le** | yuva420p10le | — | — | — | — | — | — | — |
| `db7a347d...-P` | **yuva420p16be** | yuva420p16be | — | — | — | — | — | — | — |
| `9c4252de...-P` | **yuva420p16le** | yuva420p16le | — | — | — | — | — | — | — |
| `14b664f7...-P` | **yuva420p9be** | yuva420p9be | — | — | — | — | — | — | — |
| `647f7a7e...-P` | **yuva420p9le** | yuva420p9le | — | — | — | — | — | — | — |
| `58ab0ed2...-P` | **yuva422p** | yuva422p | — | — | — | — | — | — | — |
| `83acd17a...-P` | **yuva422p10be** | yuva422p10be | — | — | — | — | — | — | — |
| `c0b9d15f...-P` | **yuva422p10le** | yuva422p10le | — | — | — | — | — | — | — |
| `f792517f...-P` | **yuva422p12be** | yuva422p12be | — | — | — | — | — | — | — |
| `7885309e...-P` | **yuva422p12le** | yuva422p12le | — | — | — | — | — | — | — |
| `044ad9d2...-P` | **yuva422p16be** | yuva422p16be | — | — | — | — | — | — | — |
| `48dcc721...-P` | **yuva422p16le** | yuva422p16le | — | — | — | — | — | — | — |
| `cfb1840b...-P` | **yuva422p9be** | yuva422p9be | — | — | — | — | — | — | — |
| `80131528...-P` | **yuva422p9le** | yuva422p9le | — | — | — | — | — | — | — |
| `37dd5de0...-P` | **yuva444p** | yuva444p | — | — | — | — | — | — | — |
| `ace10291...-P` | **yuva444p10be** | yuva444p10be | — | — | — | — | — | — | — |
| `c460285e...-P` | **yuva444p10le** | yuva444p10le | — | — | — | — | — | — | — |
| `ac9076e2...-P` | **yuva444p12be** | yuva444p12be | — | — | — | — | — | — | — |
| `fb199e42...-P` | **yuva444p12le** | yuva444p12le | — | — | — | — | — | — | — |
| `380644ae...-P` | **yuva444p16be** | yuva444p16be | — | — | — | — | — | — | — |
| `68729143...-P` | **yuva444p16le** | yuva444p16le | — | — | — | — | — | — | — |
| `8e0a7235...-P` | **yuva444p9be** | yuva444p9be | — | — | — | — | — | — | — |
| `14f549af...-P` | **yuva444p9le** | yuva444p9le | — | — | — | — | — | — | — |
| `675e4fb0...-P` | **yuvj411p** | yuvj411p | — | — | — | — | — | — | — |
| `cf17433d...-P` | **yuvj420p** | yuvj420p | — | — | — | — | — | — | — |
| `df122b92...-P` | **yuvj422p** | yuvj422p | — | — | — | — | — | — | — |
| `1684fd14...-P` | **yuvj440p** | yuvj440p | — | — | — | — | — | — | — |
| `b77ea6ba...-P` | **yuvj444p** | yuvj444p | — | — | — | — | — | — | — |
| `13842c35...-P` | **yuyv422** | yuyv422 | — | — | — | — | — | — | — |
| `6334770d...-P` | **yvyu422** | yvyu422 | — | — | — | — | — | — | — |

### Audio Sample Formats

| UUID (Type-Suffixed) | Canonical Name | ffprobe | libmagic | puremagic | pyfsig | binwalk | rawpy | Pillow | exiftool |
|---------------------|---------------|---------|----------|-----------|--------|---------|-------|--------|----------|
| `0f05e3cb...-S` | **dbl** | dbl | — | — | — | — | — | — | — |
| `a9e29bfc...-S` | **dblp** | dblp | — | — | — | — | — | — | — |
| `a54d0973...-S` | **flt** | flt | — | — | — | — | — | — | — |
| `5dce2525...-S` | **fltp** | fltp | — | — | — | — | — | — | — |
| `d82de5f7...-S` | **s16** | s16 | — | — | — | — | — | — | — |
| `9e2f723b...-S` | **s16p** | s16p | — | — | — | — | — | — | — |
| `31b6ad94...-S` | **s32** | s32 | — | — | — | — | — | — | — |
| `f85ac22b...-S` | **s32p** | s32p | — | — | — | — | — | — | — |
| `eae29e63...-S` | **s64** | s64 | — | — | — | — | — | — | — |
| `28480542...-S` | **s64p** | s64p | — | — | — | — | — | — | — |
| `79a0938d...-S` | **u8** | u8 | — | — | — | — | — | — | — |
| `fb8a3408...-S` | **u8p** | u8p | — | — | — | — | — | — | — |

### Audio Channel Layouts

| UUID (Type-Suffixed) | Canonical Name | ffprobe | libmagic | puremagic | pyfsig | binwalk | rawpy | Pillow | exiftool |
|---------------------|---------------|---------|----------|-----------|--------|---------|-------|--------|----------|
| `9f0b415a...-L` | **2.1** | 2.1 | — | — | — | — | — | — | — |
| `b85b3b9f...-L` | **22.2** | 22.2 | — | — | — | — | — | — | — |
| `03fa9289...-L` | **3.0** | 3.0 | — | — | — | — | — | — | — |
| `069e56e7...-L` | **3.0(back)** | 3.0(back) | — | — | — | — | — | — | — |
| `5e84d5b4...-L` | **3.1** | 3.1 | — | — | — | — | — | — | — |
| `e2dadd02...-L` | **3.1.2** | 3.1.2 | — | — | — | — | — | — | — |
| `1c0266a4...-L` | **4.0** | 4.0 | — | — | — | — | — | — | — |
| `b3012f1e...-L` | **4.1** | 4.1 | — | — | — | — | — | — | — |
| `802ecc25...-L` | **5.0** | 5.0 | — | — | — | — | — | — | — |
| `9a38ce29...-L` | **5.0(side)** | 5.0(side) | — | — | — | — | — | — | — |
| `0f74c57c...-L` | **5.1** | 5.1 | — | — | — | — | — | — | — |
| `69597858...-L` | **5.1(side)** | 5.1(side) | — | — | — | — | — | — | — |
| `74301fdb...-L` | **5.1.2** | 5.1.2 | — | — | — | — | — | — | — |
| `2dee444e...-L` | **5.1.2(back)** | 5.1.2(back) | — | — | — | — | — | — | — |
| `ba4d56a3...-L` | **5.1.4** | 5.1.4 | — | — | — | — | — | — | — |
| `b1a67332...-L` | **6.0** | 6.0 | — | — | — | — | — | — | — |
| `9994a054...-L` | **6.0(front)** | 6.0(front) | — | — | — | — | — | — | — |
| `683efc40...-L` | **6.1** | 6.1 | — | — | — | — | — | — | — |
| `37d01fd9...-L` | **6.1(back)** | 6.1(back) | — | — | — | — | — | — | — |
| `641d67da...-L` | **6.1(front)** | 6.1(front) | — | — | — | — | — | — | — |
| `ff97c52e...-L` | **7.0** | 7.0 | — | — | — | — | — | — | — |
| `3f39ab23...-L` | **7.0(front)** | 7.0(front) | — | — | — | — | — | — | — |
| `9e1b4b6e...-L` | **7.1** | 7.1 | — | — | — | — | — | — | — |
| `cc1a0e0e...-L` | **7.1(wide)** | 7.1(wide) | — | — | — | — | — | — | — |
| `0d3ad488...-L` | **7.1(wide-side)** | 7.1(wide-side) | — | — | — | — | — | — | — |
| `82d3d25d...-L` | **7.1.2** | 7.1.2 | — | — | — | — | — | — | — |
| `a3ab12ca...-L` | **7.1.4** | 7.1.4 | — | — | — | — | — | — | — |
| `f475b83f...-L` | **7.2.3** | 7.2.3 | — | — | — | — | — | — | — |
| `d777844a...-L` | **9.1.4** | 9.1.4 | — | — | — | — | — | — | — |
| `2fbf2db7...-L` | **9.1.6** | 9.1.6 | — | — | — | — | — | — | — |
| `09899e01...-L` | **binaural** | binaural | — | — | — | — | — | — | — |
| `171302fe...-L` | **cube** | cube | — | — | — | — | — | — | — |
| `5a88dc9c...-L` | **downmix** | downmix | — | — | — | — | — | — | — |
| `10b22873...-L` | **hexadecagonal** | hexadecagonal | — | — | — | — | — | — | — |
| `0627cfbb...-L` | **hexagonal** | hexagonal | — | — | — | — | — | — | — |
| `99799511...-L` | **mono** | mono | — | — | — | — | — | — | — |
| `bdcfb498...-L` | **octagonal** | octagonal | — | — | — | — | — | — | — |
| `9ef0ea6b...-L` | **quad** | quad | — | — | — | — | — | — | — |
| `4bf0d2b7...-L` | **quad(side)** | quad(side) | — | — | — | — | — | — | — |
| `8e57bfa8...-L` | **stereo** | stereo | — | — | — | — | — | — | — |

## Full UUID Reference

Complete UUIDs for all formats (expandable for copy-paste):

```

# Container Formats
40fcd791-c5ae-5eac-89f2-20af4690424d-C  # 3dostr
093583c1-6f88-541c-96f7-8adb5f132a43-C  # 3g2
84d2205f-0db6-5d0d-a413-accb652867f2-C  # 3gp
f2f5f78a-aadd-5f48-bf47-f7f6f9fe2e9a-C  # 4xm
f578d3a9-49b8-53c4-8a9c-65719c8b46c3-C  # a64
1157f31d-5626-584e-8134-ea90859d4f52-C  # aa
458ed14d-ff8e-5ad0-89fb-90c949a757e9-C  # aac
b530501d-c02d-53fa-a22a-b47ccd9e60fd-C  # aax
50f7d473-9416-5741-b773-bd1b70015886-C  # ac3
68f9acfa-c320-57e5-8fc0-e1279bd2d943-C  # ac4
7e94db15-98fa-5e3e-8f98-b330ee2fe87e-C  # ace
cedaf28b-1603-5898-bddd-9a0d5e36f595-C  # acm
3adf5932-07fe-52c6-8cf0-c4839c35cb6c-C  # act
45e4ac25-e1e9-5efd-82ed-d5ac2dcd7dee-C  # adf
81628ae6-a0d5-5bbe-91a2-60afd1135062-C  # adp
6f9cb1d7-e1da-52c6-b34c-0c4bcd8765b1-C  # ads
17c9dafe-07c7-579e-882f-ad2cd90374eb-C  # adts
e0836bd1-dd89-57de-94ad-d99c9d29ca8d-C  # adx
7ae3a862-7e70-5a8a-a14a-020fe32f8849-C  # aea
72519a24-8b84-531a-a4ba-12e74aa8d388-C  # afc
6ef0d275-1569-5516-80d0-855878671046-C  # aiff
5f9e5eb3-029a-5d11-a162-d643b83b01b2-C  # aix
5b313ba8-f6f3-5b2f-a889-2fff9cbe9ebc-C  # alaw
d3fde19d-b041-5512-93b4-d87d71225edf-C  # alias_pix
5b4e0fc0-81f6-5628-8735-05c4d55c448f-C  # alp
af78d65e-b513-51f3-a1cb-ca5ae0240dcf-C  # amr
235eed17-7d6b-5dbc-8155-dafc7773c453-C  # amrnb
adc89d46-9aee-5a4a-b931-110e2ab7e11d-C  # amrwb
ec731d26-948a-54e8-b33b-172b82ed53c5-C  # amv
346c0137-9d0e-5ebc-97b1-0d5aa73f30f9-C  # anm
526b9cd2-d991-56b7-99af-b39d44602b3b-C  # apac
c6e453be-7db2-5432-ba24-c15fbede4371-C  # apc
115cae10-8aac-52ac-9cbc-de30eb5ee738-C  # ape
8d1fdcbc-99c4-5ac3-8b4d-57d2e25fb32a-C  # apm
551a7fed-8d9f-5c85-b901-034cffeeb01b-C  # apng
8caebe0d-e83d-544d-9e00-b925d96695da-C  # aptx
d7b2fd94-b605-588b-af15-9c01f9963a64-C  # aptx_hd
f11b76d1-07f8-5e60-9edf-bdd04f5f72bc-C  # apv
46ab3f2c-7a68-5a9a-9247-151862c7aa33-C  # aqtitle
ed37289d-fb84-5e64-82f8-27b2d3b03356-C  # argo_asf
62f6a35d-dad0-5be4-bb71-0bde1facbb2b-C  # argo_brp
a2c131ca-d67e-5e71-99a0-a8ee0435bfbd-C  # argo_cvg
7f630cd5-9dd6-520d-9a38-d98a6895d227-C  # asf
2b6395b9-a64f-5de4-bcd9-add5c6f4b25c-C  # asf_o
2aac53d3-8189-595d-8901-ad91578fb854-C  # asf_stream
4a6aca20-be85-5e97-83a0-73e330d45f9d-C  # ass
cde169a2-e38e-5470-8a3c-eeba65e2c62f-C  # ast
31e56ccc-749a-5f8f-ba70-f1ab9f8f9850-C  # au
bc40c757-b87b-5ac6-8432-6e8136b781bb-C  # av1
c7fd4386-20fb-5f59-8df2-c081da124546-C  # avi
2f6ae690-f8ae-500f-898a-baa9f7452a50-C  # avif
d8a8630c-3c80-5a9a-b4d9-9569d558191e-C  # avm2
a157a83b-4acc-5462-8e58-7a6bf7e25470-C  # avr
dbc846d9-8d02-57ff-8e26-e84390e93fee-C  # avs
71ee3b3f-88c4-57a4-8eed-db52114e283c-C  # avs2
2e8de15b-a7f6-5341-8403-f00475de1f8a-C  # avs3
2db10a7b-c5d4-5837-9a43-5105cf71434d-C  # bethsoftvid
4ce63896-fd36-5a8e-9a02-dcc4b6d6b46a-C  # bfi
3e5cbbcb-bb99-52a9-8904-292ad57db51b-C  # bfstm
1fb786d8-9223-53f6-9dd7-95b9b1e3f8ff-C  # bin
21248660-da4c-52bf-99fd-6e3079f76b2e-C  # bink
afbe6df4-e5ee-56f7-9722-dd2ae923a44e-C  # binka
a49c45cf-02b4-5993-a45c-72c1d826edab-C  # bit
1cdd3f54-0ee8-5d5f-9466-3af7ec084d1f-C  # bitpacked
6254e908-bf9f-5b78-954b-ba500aad2e76-C  # bmp_pipe
b7c9db34-1521-5486-bb55-813efec4b39f-C  # bmv
c1393756-ac40-50f3-8405-c130439fdf35-C  # boa
58eb151e-3380-5533-a5e7-488131c3b339-C  # bonk
76b546b5-17da-51c8-a75a-3b796e0ef2fa-C  # brender_pix
7a730854-fcdf-59b8-a048-f1d16cecc3e6-C  # brstm
c1696193-5b1d-5fc9-8c99-bfb8044acfae-C  # c93
74fd0a26-86d3-5bcf-9adc-8d326fea9814-C  # caf
9d414937-cbfd-539c-b40b-133466c5235e-C  # cavsvideo
e92865b8-f350-51ec-810d-695b37d66aeb-C  # cdg
8137661d-bcef-54a8-bc5b-3197703d65c2-C  # cdxl
fb566510-abad-57fe-8af3-f4affd5b52f0-C  # cine
c7602580-e7fe-527f-89f2-4b4c55f5b1aa-C  # codec2
b238b2bc-c619-543a-a14e-11503ce68a96-C  # codec2raw
a499ab45-4525-5acf-9b77-d4101c27169d-C  # concat
42f95fa4-b9b3-5b93-a5b0-07e304a8ddbe-C  # crc
3964eaa3-2c48-5ec8-a343-7dbf738339f9-C  # cri_pipe
ad5f5e58-b717-5388-8ed8-515f15c3ba7a-C  # dash
1d281805-486f-5390-8dd4-7d56b7aff56f-C  # data
03b03c45-e574-5060-a7cd-4eaff71d5c68-C  # daud
dc18cfbf-3cc3-5172-8a7e-8d3a5257fb42-C  # dcstr
23f732fc-00e3-505e-950f-b206564398ec-C  # dds_pipe
74a6ac7a-29ca-5697-aa27-e30088fac2d9-C  # derf
74f3b48e-0a6f-568f-97fa-d406da0709c7-C  # dfa
92e05a5c-8f93-5572-a525-6754868dc895-C  # dfpwm
39095877-5238-50f8-a6ae-05bcb94fe66f-C  # dhav
48832084-91ee-56cd-aa60-810da7364c4a-C  # dirac
74c11481-379d-59e2-9c51-d4e255cdc08d-C  # dnxhd
74e108b7-2985-5f4a-8cd0-1581a71c1145-C  # dpx_pipe
63b3f7b9-0269-55d9-ae1d-33597cc652a8-C  # dsf
af77a0cb-63b9-55cf-a7ac-47f709e6f0a0-C  # dsicin
f727aabd-ec81-54ca-9f2f-b467eaa57c7c-C  # dss
7a7276a5-35cc-5af1-9857-e59d66e0c9d2-C  # dts
5dd947c2-99d2-5b6e-b909-0761085ca0a0-C  # dtshd
ded71677-d363-5f34-a073-7cb8543820b4-C  # dv
017c0a52-b5b1-5691-8306-18be0617bcc1-C  # dvbsub
b9d61a31-4154-5536-aaad-d46fe985bddc-C  # dvbtxt
e23f2f57-2a28-560c-8a6e-79d9c5ce3639-C  # dvd
6e8a6c82-37c8-5195-a00d-ee1afb461291-C  # dxa
fae217fd-cc51-533e-b26e-d04fbbc906a1-C  # ea
ca8a8662-6c35-5f41-8469-69f04084d9f3-C  # ea_cdata
1dd0b283-7248-5a8d-9ded-e2ad83815246-C  # eac3
09f5e04a-e702-5a76-a749-6050e7d2eac2-C  # epaf
f2674f95-adac-572d-97b7-0dca31aed6b0-C  # evc
11468e1f-ea1a-5c19-acab-c579f9ddd6b7-C  # exr_pipe
de9b272f-b645-5caa-8db3-d76f54d8385e-C  # f32be
93f93bd8-07dd-599b-a358-7c7910528bac-C  # f32le
9dc3da9d-5f5a-5705-a4b8-9461f70b6fde-C  # f4v
a2c3dd12-a4e5-5598-845f-367e1e32eb5f-C  # f64be
67214b6a-45dd-5e74-b2db-1e35b479f396-C  # f64le
1322cb66-6706-562e-9f0d-7963feb1aa9c-C  # ffmetadata
fb8d3259-3842-53ed-8c2f-e965af37367f-C  # fifo
8ef008a2-c481-5dda-995f-47593bd6edd7-C  # film_cpk
c67a469a-df72-595d-bdb3-c0ffcd7fb723-C  # filmstrip
bd12d03b-a123-5641-8cc5-b2c40eaca5fc-C  # fits
bf744455-1ff1-5170-9005-b4422065becf-C  # flac
8cbe5947-cf75-52fe-a65c-e6e98751cb35-C  # flic
9127bc49-6cd3-5bfc-8348-c10003e695e4-C  # flv
a91ce192-ad85-5f0d-8f59-343db73d73e9-C  # framecrc
c3c1ad8e-688b-57df-8b1e-cd8819fe7b19-C  # framehash
3e37a0e9-03d3-5a55-a518-1a62f37fa7b9-C  # framemd5
59315f29-ea06-57a6-a524-447242edae74-C  # frm
171d64e3-e5d1-5115-b543-c0a99d1bdc92-C  # fsb
70d4ec7b-a51c-5b46-a6e8-cfc209713367-C  # fwse
c3997b9a-4ef3-5786-b052-23182b07f86a-C  # g722
8765e7e1-c8bf-575b-a6b0-a737506ddf65-C  # g723_1
cc3e176b-0a19-5752-baef-2c4b745ceb60-C  # g726
08f389d7-3d48-5c5c-97ea-b0b94e4e1ebe-C  # g726le
2f59e7ce-d3a7-530b-8b89-b295f77dcda5-C  # g728
32d26757-fddd-5179-aff2-7a541247ad07-C  # g729
9cc60da8-3aef-5625-baea-981faef9c3fd-C  # gdv
2b17ad4e-55ed-5f69-9349-79d9b28fe3fd-C  # gem_pipe
ba93a271-bfb6-5249-8792-218bde210240-C  # genh
80645058-89ea-58e5-af4f-efaba9041e8f-C  # gif_pipe
095e1cab-9d65-502a-bdbc-41c56f642db3-C  # gsm
676d5e79-4e0e-5eaf-b503-1e82cd516c6c-C  # gxf
751b9707-a16c-51dd-a522-b1c96fedd1d5-C  # h261
6e20a312-6f70-5763-8c8d-3070dd86a420-C  # h263
d6ea65a0-5a97-5d44-9b71-1dfa6796b4ba-C  # h264
adac47a7-7163-588f-a5e8-078faa83d55f-C  # hash
698ef80b-07ca-53f3-946a-1715c9463d46-C  # hca
fde8de79-1851-5529-9ec8-8f036186cd59-C  # hcom
c874e9e6-4f6d-5a3b-a33a-32da6b5d4f18-C  # hdr_pipe
aaa6c97a-6311-5fec-b718-9ff9aef338f5-C  # hds
4aa64d23-699e-5d2f-a238-444458690da5-C  # hevc
2408a626-7437-51c8-abfc-f79229a6f01b-C  # hls
85423c91-fb4f-54cc-818d-0b709dd7b711-C  # hnm
d2520a8c-f4a5-55dc-bf2d-323b7770787a-C  # iamf
251d95c9-c1c5-50f7-9d3f-c30ecf752864-C  # ico
2dd7b22f-4dc6-5826-8ed7-96745f929b44-C  # idcin
33940393-83b3-5c22-9831-b77d99b3a751-C  # idf
f4dff553-88c5-5bcb-837b-d949b864c0b0-C  # iff
f44051da-82b0-5294-94a2-ac8ace8329ab-C  # ifv
4a9cee6e-de89-5342-a4f5-0e947792627e-C  # ilbc
52c9f5e1-fefb-56d3-ad69-4fb10584db60-C  # image2
ac0df839-5b22-5046-9134-e0c396f6cda3-C  # image2pipe
e02de780-2ca4-5564-b29e-67e45e5181e2-C  # imf
eaa626ae-da7b-5cb0-afb4-a14af92f13cd-C  # ingenient
7fb1385c-8ca1-5b30-a982-e111f1984144-C  # ipmovie
e090f758-b914-5bbc-b9a1-b8f9aeb47f27-C  # ipod
71903719-df9e-579c-be4f-57113a370c54-C  # ipu
d64a27cb-0ba4-5c7c-8817-b8143fc0128b-C  # ircam
f9debd09-d3b6-5e60-99f3-5bd8caa97698-C  # ismv
42ded3bf-a02a-52c7-9cce-bc6ecd5827a9-C  # iss
f909600e-f3d5-5a66-9306-421b062539f5-C  # iv8
89d5c5a7-aea6-5869-b0f1-418247771281-C  # ivf
e1918d9b-c1a3-52bc-965f-17701c8d9417-C  # ivr
02782949-2b37-5464-9603-811fc453f341-C  # j2k_pipe
8910696a-3cf0-5327-8776-4a6fbfdef1f7-C  # jacosub
4c51fe44-bfa8-54db-bfee-e830756c9179-C  # jpeg_pipe
c227e463-afde-56be-815c-517c77bfe8e4-C  # jpegls_pipe
f028add4-a352-5e8d-9dd9-9b011f29c29e-C  # jpegxl_anim
6d64a899-ed81-59ff-893e-39bc6acdec1a-C  # jpegxl_pipe
fe716ed5-e2da-5413-acca-3492074b1d67-C  # jv
3f9cf970-7692-5109-ac33-471c5f57bb17-C  # kux
e57642c0-fad0-5eb1-9bac-726b60bd667c-C  # kvag
c8566b86-1b0c-5061-96ea-62efdc388a8a-C  # laf
3af8f743-b660-5af4-98b8-a20de60b04ec-C  # latm
15a8172f-fe00-53f7-839c-a7432a7365aa-C  # lc3
5c9e3ac0-f018-5f58-bca2-3716257766d8-C  # live_flv
5ce2d4d3-4d24-509b-ba52-838a25114187-C  # lmlm4
3c0d176c-737f-5b63-bea3-1a559e0cff74-C  # loas
0973adb4-5096-5b4d-8471-5c724ceed10c-C  # lrc
6b1c67bd-e512-5381-87d0-66773cb24fab-C  # luodat
078af735-6c71-5f7e-8523-5c24cc4bccf5-C  # lvf
f33ffc39-a55c-5fec-907e-80cab1bd11f6-C  # lxf
eeca0b04-4624-5aef-bf6a-ea0ddee503f4-C  # m4v
2a465d03-084a-5e35-85ea-3a050dd8daf7-C  # matroska
3329a0a3-0df8-52f0-8d04-52b01cf14f28-C  # matroska,webm
1d4e99ce-4286-5451-bcaa-ed0edbf2ce3d-C  # mca
0c7deaf4-8db6-546b-868b-ef41563cb1bc-C  # mcc
98f2297a-5923-50f9-85a2-52f01b92301d-C  # md5
db15bd06-0c55-5939-9e37-194cf47eacf9-C  # mgsts
0a71b86b-824c-5576-9298-d5a9dcada909-C  # microdvd
f6a88d38-99c8-56ab-bd66-036f93a71f4d-C  # mjpeg
bf7f3b3e-e199-53cc-ab6e-9a83bef40bd5-C  # mjpeg_2000
fb79e10b-80d9-5cc7-8db5-95ab9c621bc6-C  # mkvtimestamp_v2
b2364ba9-10c7-5fc8-93fd-100af03dc18b-C  # mlp
ef5d93ea-d29e-5f49-9135-3d8b709803a3-C  # mlv
73581bd2-3caf-5353-82c1-553908e7d62f-C  # mm
f1b513a9-eb4f-5f32-8819-d04fa456152d-C  # mmf
140323aa-2e06-5ae4-b33c-8331d457ee73-C  # mods
672f1b78-ca5d-5f5b-ac73-7fe5a891a5a6-C  # moflex
3f8a2874-1b17-5dd6-b51f-fb0e7d34022c-C  # mov
759bb7b6-3ada-5c85-9901-2a86ee88f764-C  # mov,mp4,m4a,3gp,3g2,mj2
053b33fb-fdbf-5cec-a789-8b0baaa4cbb3-C  # mp2
0ca0edce-d35a-597b-985b-aa183c9d0e0a-C  # mp3
a9457602-d9c2-5787-a3f4-a6c1f72ac82a-C  # mp4
8940cfbe-cb6e-5256-8853-679d9e5fbeaa-C  # mpc
e09dd7c3-bb02-5343-9995-16540b94de91-C  # mpc8
64232332-29e5-58b9-a467-7825e2c5ac7f-C  # mpeg
661339ba-928b-57b8-8b60-b525d2935554-C  # mpeg1video
7dabad2b-02f5-5a1a-b423-ef5e11fe86fe-C  # mpeg2video
64d1e20d-f341-5ae8-9ee5-71a8a3d073f1-C  # mpegts
2c25d300-3354-5ddb-bc97-15394d637f88-C  # mpegtsraw
b4e7232c-8a04-594c-a9b4-d43dabe83249-C  # mpegvideo
82780d05-4d44-5aee-a55d-c0bbcd136820-C  # mpjpeg
c11d99ef-cb46-5a71-aa88-9ffbbead135c-C  # mpl2
d964dcaa-d18b-5ee0-89bc-4d317dca85db-C  # mpsub
0211f0b7-ec8b-5770-b566-0f968093715c-C  # msf
7e929e6b-e503-51ab-8625-c961bfeb3821-C  # msnwctcp
12528eba-ae7c-5620-9d39-8070da0f3947-C  # msp
1dafdb92-a1d9-54e5-bcc4-44a8eeda1484-C  # mtaf
cdb888a7-f8a9-5a9d-af80-a4d80d32f969-C  # mtv
6bfa7edf-ae13-5f32-9aa9-5e80dadc2b52-C  # mulaw
b4f8133e-318e-5448-910d-f0a11e6c3abd-C  # musx
e8635cfa-d015-5ec0-ac9d-7c0e346bf076-C  # mv
0755b281-9a58-5b4f-9f6b-af69cb403d00-C  # mvi
f11cebfe-21a4-576a-976c-e613600c126b-C  # mxf
6265a217-77a0-5005-9dc4-7c4d1ddbc9df-C  # mxf_d10
824b66ea-166f-5b51-b921-eac18da762ba-C  # mxf_opatom
167fdf5f-c938-5e98-bec4-44d9fdccfa33-C  # mxg
dfce1cd2-7601-571c-830f-df2385b33e99-C  # nc
a794982e-c7a9-5e3a-8ea0-41c524bc1420-C  # nistsphere
b7da877e-84ab-508a-91f8-dce05fce0018-C  # nsp
f8f9754f-a033-56c3-8837-1ea8ccba1a58-C  # nsv
46c227c2-78e4-5c33-8bdc-de676dbf34fa-C  # null
1b232105-d460-503b-b3e0-ead530b7e04b-C  # nut
f7bb07f1-c36c-5480-961a-c5bda0484ded-C  # nuv
4a188339-72d6-5fc1-a092-a0b42fbc5113-C  # obu
ab7765ba-b4f4-5e5c-aad1-8d103b688043-C  # oga
d3238328-4fa3-5601-9172-32e1017b3def-C  # ogg
f291a488-02e3-5fc0-a196-fd98f66ba8bb-C  # ogv
efd4e2cc-6a4e-5adb-ac64-769d891001c5-C  # oma
447f60b1-804e-5548-bef9-315b9370b874-C  # opus
9fcdf8b6-3d68-5017-bea4-56fefc110d70-C  # osq
80dc11c9-d078-5c9b-99d9-3c1628a6ded3-C  # paf
76511930-ea28-5db2-bc5d-0e1f83008364-C  # pam_pipe
c2dd3d19-6e97-5ef0-9169-466382216559-C  # pbm_pipe
b4e4fd2b-c08f-56e7-9c50-a6fcd1ef2ef7-C  # pcx_pipe
9ef7fc47-5fdc-5eb1-8823-7b91a5b3ad03-C  # pdv
5f4db972-f9e2-532a-8175-2e129a2e4061-C  # pfm_pipe
f4c8ce00-6376-5d65-9e97-c99ee3c2217d-C  # pgm_pipe
4a367e7b-4338-502f-b5a4-df5084036d22-C  # pgmyuv_pipe
0abffa86-896f-56af-91cf-767b9b6450dc-C  # pgx_pipe
c3aa16a3-88c3-50d1-9f86-b5d726f18175-C  # phm_pipe
3ea52f3c-ba5d-58ba-8a5b-f4c22e5ffd50-C  # photocd_pipe
aaf9a2ce-bf0a-59a0-816e-5fdb22d525ed-C  # pictor_pipe
7ffbf711-bff8-56b6-9415-5b240390830c-C  # pjs
508a328b-a595-5871-a6dc-de50916a64c7-C  # pmp
5039ee0f-c924-5540-b178-cb9e0ad3210b-C  # png_pipe
04beb324-0c3d-5e0e-a3ac-c697a38367d8-C  # pp_bnk
c98bba6d-8f4c-5b0f-bdf8-18ba9b795ede-C  # ppm_pipe
92f139a3-13f5-5b70-8662-f3d78c23ddb5-C  # psd_pipe
026f3c37-9e47-530a-ab19-58c03876bc49-C  # psp
2cb4bf29-8dbd-5c46-b362-c7f47a11c37f-C  # psxstr
3068c5a0-074e-5079-b1a5-9da54b36d487-C  # pva
2e74785c-3a5d-5e92-abd3-50ea7e43a395-C  # pvf
f1cea715-1a40-596c-b6d2-7ce01c8c542c-C  # qcp
21d01a06-7cc1-5a33-ad68-abcdc4d38de5-C  # qdraw_pipe
7334275e-8fdd-5aed-99f6-939a665af38a-C  # qoa
537f3521-b9eb-58ff-a000-80ca453e3b6e-C  # qoi_pipe
db824543-e659-528a-850a-10c93374e662-C  # rawvideo
475743ce-aa2a-5e1e-be76-b843583d137c-C  # rcwt
05b808e0-5cfe-58b3-9191-d959a3e8f6f2-C  # realtext
ee3f41d2-1216-54b0-b9ee-892d600dc7ee-C  # redspark
a6aa315f-b6a6-5232-acf3-60bb462aea2a-C  # rka
8820a7ae-7284-52a8-9384-227b56f04594-C  # rl2
1eb7e7fe-2ecd-5717-bde4-a9e4daee029c-C  # rm
0a4a5837-78c9-5bbf-b982-080dacf22cb4-C  # roq
ab1a8013-9131-531a-a915-012e482d5f33-C  # rpl
1523b500-d39f-5c23-b240-246a41282b77-C  # rsd
3353e35c-c67c-5d3d-909c-7dd43cd5fee7-C  # rso
8bcef317-4421-54cb-a239-c18e1a4e2151-C  # rtp
dcf2069e-cfb6-5de9-abb9-6a2bfacffe8b-C  # rtp_mpegts
797aa974-a72b-5229-b96f-2236446978d1-C  # rtsp
616a3783-0052-5440-ab2d-42dc03d6a45b-C  # s16be
337ad944-cdf5-5042-9ffc-604365bd20c3-C  # s16le
ec46128f-7d2e-5141-ade9-0a6cd8e4e793-C  # s24be
b3116c5c-2ff2-5cf9-bbf4-06690da7ddd8-C  # s24le
be8fe302-fe38-5787-9209-615398e001ef-C  # s32be
7d022f7e-0fa9-57ba-91f2-cd6df36048cf-C  # s32le
531cf635-b56e-5a45-894f-ac05f654dee3-C  # s337m
a882166a-f98b-5875-b4bf-7beb1bd0d3ae-C  # s8
d90b259c-8b40-58e2-9d99-94817ad0f882-C  # sami
060dd15a-940e-51a8-90e6-a547658b2a2c-C  # sap
187ed794-c5e4-5b16-ae52-ccc4ba0f3f43-C  # sbc
96233e8d-65f2-5da7-ab7f-2ec23fd79c3a-C  # sbg
3ea72426-bf7b-570e-8b65-0e5b2c201a28-C  # scc
e5ccd098-2afe-5694-b236-ef25fcf798df-C  # scd
fba1d08d-8c01-5957-84f2-83c049611696-C  # sdns
da512b2f-01e3-5514-a94f-1daafe311cc7-C  # sdp
d3e3ee55-30fb-56e4-857c-7fdae35aad2d-C  # sdr2
ed4f1900-5c2a-5946-9b22-329b7888e273-C  # sds
b6f95b58-04df-5345-80ec-80cd5371fd8c-C  # sdx
ac055043-3c01-5b25-90dc-f11c03aa27c5-C  # segment
4ce6ba6e-d1d8-5daf-b9ca-eb3c58bf6851-C  # ser
c3aa3b80-6bcc-576f-98cb-33387854d0ce-C  # sga
da554093-b44a-582f-8537-b5bc2cf0ddd0-C  # sgi_pipe
995f398c-97e1-53a0-b325-acb8a3669b70-C  # shn
6c95549f-b94c-5e04-b4b4-b6f2f146c849-C  # siff
5f65238e-fb75-5937-979f-30efeab6a978-C  # simbiosis_imx
6f61e170-9125-5978-bd20-bad28fb6925a-C  # sln
39a54154-83dd-5a13-8986-d7eaf350b243-C  # smjpeg
f5828f43-f9c9-5659-a738-1ee7fff8a19d-C  # smk
f43c145b-4cc8-5727-93a7-daa7773e60da-C  # smoothstreaming
d1d8d935-05b3-5845-b4bb-b4105d934d29-C  # smush
9160f005-5718-552b-98ec-b1415d9e9e16-C  # sol
1d736177-9a88-5796-8013-fcc8e9018b97-C  # sox
8bbf425d-547b-52b6-9f5e-43227dae2c52-C  # spdif
823e4c9b-908c-5ab8-923b-731c23b479ad-C  # spx
2d9dd1b2-f273-5a2b-af04-b250cc186ac8-C  # srt
c9d6c414-e3f1-5142-ab3e-8cbfd8dd1ff1-C  # stl
7a4a44aa-b424-59ec-a6b7-26b705f17b60-C  # stream_segment,ssegment
fba042dc-537a-5fc1-856b-cb222ce296c1-C  # streamhash
9f050517-f517-54cb-bae8-dfb13e949e30-C  # subviewer
415fc2b5-28a5-5198-843d-968e08c51ec5-C  # subviewer1
ab762315-5217-57b5-86fa-a787547d4876-C  # sunrast_pipe
cec5a159-d0c4-5a0b-8ff2-93d08e1dbbd7-C  # sup
deeb6e29-ee09-5562-9cec-fe3f987f2ea4-C  # svag
d685525d-3781-5d52-bc6f-7528ab8ec37d-C  # svcd
84321957-2aa4-579c-9fd3-7f4cf8bdb6ba-C  # svg_pipe
33b7109e-88d8-55e6-9591-9b1b60236909-C  # svs
b1c9f4aa-c775-5e26-8644-f023bee8b9ed-C  # swf
983acf7f-7cc1-512b-8639-939a11ca1b57-C  # tak
67fc34b3-8efb-572b-b4bd-a300f6897e6f-C  # tedcaptions
ea6aead1-04b5-5eec-aa4a-1a212688cf49-C  # tee
d8ef3601-e26e-5b36-9f9a-a8ac75767cee-C  # thp
73a753d2-35cb-53d5-b4bf-53c9664c38d3-C  # tiertexseq
320b80dd-693e-5472-8ad5-d4689cb7c740-C  # tiff_pipe
a39f2552-cc22-5147-8500-c30a82e6247e-C  # tmv
68cbc40c-230c-5a29-8d8c-c71a19fee193-C  # truehd
85ad801b-b0da-58aa-a730-4adfca0170ba-C  # tta
62d9b169-c4a0-57a1-b3d2-60feaa5f4dca-C  # ttml
2b929086-b8f0-59d8-a26f-0c11dce60cb6-C  # tty
d441ea77-27c1-5b00-a881-54bb2f345a9c-C  # txd
a8423078-0eba-5f6d-9137-24e549b54178-C  # ty
ffbfbf26-003a-596f-a0d5-6bfaad295255-C  # u16be
afed4088-217d-5939-8283-58281f20dab2-C  # u16le
4148d717-8f6a-56a9-bf43-7a831fed5f7a-C  # u24be
11e0a5f1-8ad5-555b-ac52-89b2334e377a-C  # u24le
cb8afe1c-8ae4-598f-aeba-fdcfedfee08a-C  # u32be
cbf5aaf1-8b06-5fa0-a942-37f6fcc2cc4d-C  # u32le
0f45e7c5-c5fe-545b-87b8-7ded037f6a04-C  # u8
000620bc-88bf-58cc-b5b1-bb637bbfd566-C  # uncodedframecrc
76acb1d8-e2d1-57fe-ac13-d72738b34152-C  # usm
893873d4-78d6-56ab-9b58-52cfda81fe52-C  # v210
229b4a1c-ebd2-5132-bde1-5dea19b4b097-C  # v210x
37c4b278-77c5-5319-83c6-9b00860f8514-C  # vag
3a2b25dc-f7ce-525b-a8d7-a4f260661003-C  # vbn_pipe
e2f43af1-20b3-52d4-bd3f-fb2bd4b0e2f0-C  # vc1
002c6ea6-c91e-5387-bd6e-76a63de4b896-C  # vc1test
74ee2b27-6042-51ae-bc6c-569341e71d2c-C  # vcd
648d0dc2-6d48-529c-89ab-af9ee5f9fd64-C  # vidc
75ffa0ee-070d-5b7a-8c62-3147b8260798-C  # vividas
81475378-59e4-5e78-a083-da4f1d7510e1-C  # vivo
c4fb7d10-bf88-5c16-b8bd-c31b40c17e3d-C  # vmd
edcb37c8-6a3b-5979-8f3f-42b981e3a6e6-C  # vob
4e3c322a-9c3d-51a2-a79d-33a1bca488c2-C  # vobsub
b49b9891-63fc-54ce-9d86-eb6b7554f69c-C  # voc
ad6eff82-abec-54a7-84b3-6d56a972a6e7-C  # vpk
4ad73c03-c90c-5332-81cf-2e393a40ce39-C  # vplayer
1ebcccf3-f79d-5a52-8c24-54d1275cc8d4-C  # vqf
8067205d-7055-56b9-b5f6-f74723b7348f-C  # vvc
537ff079-684e-5451-8234-403f71dd099e-C  # w64
a9626ea6-7aee-5c3b-b08e-90ea879906f8-C  # wady
71ed6c49-8ad0-5226-865d-3e71fdd6c279-C  # wav
186f2a54-cd3b-5fdb-8bca-a67ae4c4e651-C  # wavarc
8d33fcbe-58f1-557a-840d-194747812819-C  # wc3movie
795dcbf5-8ba7-575f-be97-79c2d93e7b6d-C  # webm
6e6d4cb9-64b6-55f7-9e0f-38cb575dc158-C  # webm_chunk
fcc871e3-72d6-5ade-97af-d7715a885f6a-C  # webm_dash_manifest
44d212be-ea5d-5214-9e3c-ce3d2b9c28bd-C  # webp_pipe
8ac80dbd-b655-5df7-b77f-5219ae1d095e-C  # webvtt
4705a69f-0ef7-5ca7-a838-d53928740293-C  # wsaud
ac579e43-035b-52a1-8d0b-fd14f84fb9ec-C  # wsd
846ae66a-d11b-56cf-b9fa-0813e985d817-C  # wsvqa
ccf121d1-dc29-5855-b7fd-3482f66629c3-C  # wtv
4ce30147-924f-51ff-93fd-2bb9b7aa5fd3-C  # wv
ddd135b5-1e7b-5c56-b564-f51d8c87b07f-C  # wve
10c4aa6b-2c60-5d90-b6a7-c3e3dd457f70-C  # xa
60885bc3-50e8-5e39-bdc7-92ebaf0867db-C  # xbin
0c46d931-41ee-524d-9135-408f8dfaa664-C  # xbm_pipe
1cba27e5-ac12-5147-ae98-107afd5ef44e-C  # xmd
a46aa7da-077a-5019-a0d0-d77242925cd7-C  # xmv
77f88520-ceed-5ff1-be5c-961f0d370e2c-C  # xpm_pipe
3053c113-8c13-5682-bc73-c127ec08e966-C  # xvag
76f19650-8e3c-5498-8800-60015c144a2d-C  # xwd_pipe
9fbd4432-ee47-5965-a824-e6542ca85708-C  # xwma
e2f128d9-0d51-55d1-bf0e-91ac3740e155-C  # yop
59675ad9-30c6-5d2a-9a97-09765c72ee49-C  # yuv4mpegpipe

# Video Codecs
5646ca69-75f4-571c-8e9c-6742cddb3ea8-V  # alias_pix
3cf8e243-fa15-5db4-8951-2e071d5e4bae-V  # amv
575737c9-ce1d-52c0-8ca1-cc0b29be3705-V  # apng
99b1f2d0-7bfb-55ca-88f6-7b4af0bc95f4-V  # asv1
c947275d-2809-5d84-8646-1d3ccbe17d99-V  # asv2
c69693cd-1fcd-5608-a8df-9476a00cfa9b-V  # av1
e3f55e0f-9647-5a92-9ff5-8d4097a7a697-V  # avrp
7b206556-1d74-544e-90b1-2395f2500a81-V  # avui
0b299a0c-909f-5dfa-8fa4-667ac7ca2dce-V  # bitpacked
2bc02020-90b4-5b59-88dd-ce80c280d083-V  # bmp
b648cd1e-4c6e-5029-8098-af87b9e41b6a-V  # cfhd
332063c0-da67-53b5-9241-861ee8f05039-V  # cinepak
2b31543d-f3b5-5dbf-a3be-b4eb5d2be3fd-V  # cljr
71ee9d35-239b-55d8-a01c-79b23ff0d7c3-V  # dirac
d84fd63d-f633-5450-8d71-2609026042c6-V  # dnxhd
d17eedba-824c-5e8c-a52b-baf8d7b2249a-V  # dpx
301bc50a-17f4-5635-86c7-5cf7c0a15a34-V  # dvvideo
7af4fa67-efb7-5632-8cbe-a62e27b95b65-V  # dxv
a6a5d9fa-1e21-5256-8d92-6a4d3fe30814-V  # exr
6de418ad-cbff-5e5a-8542-6701e468259c-V  # ffv1
4a58899f-e37b-5eb3-b2ba-022d403c8d08-V  # ffvhuff
7edee68c-e3f3-5ef2-a457-0aae264bd392-V  # fits
6bfc16ef-2632-53f9-9168-2442e5b6c3f2-V  # flashsv
1ed7f29e-7b2a-5838-b6b1-2fe312643314-V  # flashsv2
377b6c61-24d1-5e07-b3ba-f3ad9929a0db-V  # flv1
027f3fb3-0742-597c-945d-3b2451136d23-V  # gif
3452bf5e-f05d-58d8-ac00-524c92db9879-V  # h261
ba1d20a6-3738-5ec3-af9e-2f1877b216ec-V  # h263
45843b06-cff0-5479-8f2e-43d125ac9923-V  # h263p
b2e62c4a-6122-548c-9bfa-0fcf3613942a-V  # h264
b00d4f7f-b057-5df9-8fb6-5d1b41f88e19-V  # hap
1fa2d4ca-6903-54da-b7e6-37863c52ae02-V  # hdr
faf4b553-de47-5bc8-80ea-d026a2571456-V  # hevc
b36d076f-b93b-5280-ab1c-e865061c681f-V  # huffyuv
d1349945-8b2c-5fcb-8bf8-288634a2a4ab-V  # jpeg2000
c5383a2e-407c-57ad-a0fa-0786f19a6c5c-V  # jpegls
f27384fa-30eb-52e8-83a0-e8d319f84f99-V  # jpegxl
1799f0dc-a86f-52b9-88bd-638ffde5bcec-V  # jpegxl_anim
b43b9c32-fe29-58e2-ac1c-4cfeec056de7-V  # magicyuv
082454e8-f0a6-5828-a25c-21d2e55090d1-V  # mjpeg
b90ff05b-e3d7-543e-bf1f-60ec5bf8c1b6-V  # mpeg1video
260ba350-c7f8-5bc0-a6a9-a3ee1b0f2497-V  # mpeg2video
61a6cea9-a710-5067-b362-cf5e355c33fa-V  # mpeg4
6ace59c7-51f1-5165-bb76-42e8b89feaf4-V  # msmpeg4v2
10306bcb-e0bd-56a5-a380-d4fdc6d555ff-V  # msmpeg4v3
64798a74-fc72-5ab4-b721-7406cefb6775-V  # msrle
df87246b-e14c-5a9a-ab82-cdad08bef5b3-V  # msvideo1
9be619e9-b3d2-598e-8982-13c11296b2d0-V  # pam
d7466c05-34fa-563e-bb51-80e39fc7a400-V  # pbm
94e95463-2bea-5b85-bfa8-c26fe9caf12f-V  # pcx
a0e42d70-52d3-5efc-b467-a57129ed784c-V  # pfm
b195d3ac-0355-57eb-8b20-91d798962a82-V  # pgm
a9a8bd10-4c64-587a-9d7a-9e4c9326ec63-V  # pgmyuv
4765ea09-2f03-5bc8-89f8-8d55744cf423-V  # phm
47d2f243-ccb2-5f99-a9fb-81a801a7eb4a-V  # png
390cbf23-1bff-5e27-bf04-57abb04ce23c-V  # ppm
5199d417-6877-5055-b5ba-0ec06c842c3d-V  # prores
824fc9cc-7fcf-5691-b2ea-353cfdac6e96-V  # qoi
0f71871e-515f-5c19-80ae-767c62caedba-V  # qtrle
cbc92ca3-73ab-5ad5-912f-f98eb8d1afea-V  # r10k
d104d523-0346-5ca8-83fa-3dba10321068-V  # r210
296794c5-4781-5da4-b48b-165da0674491-V  # rawvideo
eeba117d-f09b-51cd-844c-bd663eb5a509-V  # roq
ad075e0c-2ad4-5b9d-a72b-012ba7d25518-V  # rpza
c2334986-e32a-57eb-8f68-76234f653255-V  # rv10
a1526dc0-8a72-587d-9609-8a46d09dc53d-V  # rv20
a2353c6c-85b0-5638-abf6-01a2240d8922-V  # sgi
e3dba39b-dcfb-5b88-ad81-d0a1870b7a39-V  # smc
17b37aac-b497-5748-9efa-08471ea43e1c-V  # snow
9f649b3d-d7dc-50ea-beb6-263b5916625c-V  # speedhq
33e8eb6b-7694-569e-970c-4f56d875cb17-V  # sunrast
64dd14e7-5175-5e78-ad88-31859d8d33cb-V  # svq1
451a8cb4-965c-5758-9ad6-6da822dcbd31-V  # targa
8ea064ff-e9d1-5417-91dc-c4d8efa0c4cc-V  # theora
9497b0d8-4b5b-52f8-9f41-38d400252e61-V  # tiff
eec27b36-6ff4-520c-844e-66c32fc7c075-V  # utvideo
a92f597a-4e88-59c9-b754-4f502b5f71bb-V  # v210
37e0af28-2ab7-53ad-b8fe-38e117bb2954-V  # v308
a67e8f7a-e26d-5458-98e4-4f8ad40eaa62-V  # v408
48b301d7-3756-5e2f-9059-a00f66ad045a-V  # v410
9dcb9c5d-2cd0-5246-88c3-7e592ffe60fd-V  # vbn
36d3b462-a384-5149-9997-1ac6034a2d3d-V  # vnull
d91b7c22-6d8b-52a9-b17a-6eda5c3aedac-V  # vp8
4c9b19a7-ec9f-57c2-98ca-3ac8432b27cc-V  # vp9
abbe2402-ef54-554c-9086-73672ab311f7-V  # wbmp
e9b99fb3-2c1e-5c95-9c7e-cc816c8f560e-V  # webp
fc1b84c9-b86f-5e97-8b53-0bef8929afa9-V  # wmv1
7abdb54c-0427-5fb7-9353-615b023b3b52-V  # wmv2
6085b98e-d641-5ff6-bb3f-a0fb8dcae377-V  # wrapped_avframe
a81dc308-1340-5c7c-bc1e-1fbd0f7b688b-V  # xbm
cf49a3a9-913d-5914-820b-68ff6ed944cd-V  # xface
cadf6061-7ebd-59cb-a13e-c820fda21c3d-V  # xwd
a80d5ded-a3d6-5d0e-9480-eafff7b9f64b-V  # y41p
a24a39ba-aaec-5fcb-8dd2-d1bb82bee37d-V  # yuv4
febb6d8a-5bfa-5a81-825b-a39b45d218f2-V  # zlib
b8be0007-ecd9-5d05-9790-8356d6da8900-V  # zmbv

# Audio Codecs
cee232ec-97ef-5ff0-8013-4555da31bf83-A  # aac
8453c376-0ccb-5be5-b344-1e7ef82b644b-A  # ac3
8501512e-5a5e-5d9c-89c3-019e5242c12d-A  # adpcm_adx
efc63935-b940-5303-8064-f22b8b9b67d1-A  # adpcm_argo
b92cdc7c-9a0a-5aa7-90ff-8c013561a80c-A  # adpcm_g722
105ede72-94e6-55f1-96de-55fb6ef0cf0c-A  # adpcm_g726
2442f4df-afcd-5269-b35b-3052d49d51e4-A  # adpcm_g726le
85043c57-ac43-551f-a41b-d202f6985c76-A  # adpcm_ima_alp
78504cba-9f5a-5599-824e-d00deda6ad8f-A  # adpcm_ima_amv
01ee1797-44d9-501e-877b-aea84961f094-A  # adpcm_ima_apm
a054c645-aa26-56f8-bb60-ffe30a806bef-A  # adpcm_ima_qt
6407eabd-3fef-5c18-91bc-a768fb20fde8-A  # adpcm_ima_ssi
53a79661-0d1d-5b85-9676-bf3b08d3f998-A  # adpcm_ima_wav
986c5b36-9209-52dc-a722-7f9a94c0fdc8-A  # adpcm_ima_ws
9bffd6b5-9e54-547b-8851-24e549722bc1-A  # adpcm_ms
2c731eaf-e98d-54df-bed5-ccb0365ec67c-A  # adpcm_swf
532db01b-96e5-5c1a-a0bf-39ed8fb9c88e-A  # adpcm_yamaha
98638ebf-1340-5c02-a183-6be5ccf384d9-A  # alac
1df28a87-ef88-5aab-8a4b-9128fcd513ed-A  # amr_nb
542b1274-ccc7-5abc-8410-9789d138b14e-A  # anull
4c1f222f-ec80-5db0-bce9-44f4f7f87286-A  # aptx
d7588046-d004-5afa-a9ec-6677c917ac38-A  # aptx_hd
79b1fd9b-bb5b-57d4-8491-2fad67e4404b-A  # comfortnoise
10899c05-32ce-5ebe-afd6-aea9b5655e86-A  # dfpwm
b8369c87-cc93-597c-b6a6-08fcc708e5d2-A  # dts
21261078-32d0-54ef-8d6e-3d9ff429ef32-A  # eac3
1fe79ce5-27a3-50b9-a465-e1c99a234d4d-A  # flac
9f6f0ffc-1b03-5f97-bcd9-e3df17fb412d-A  # g723_1
72701c47-ab83-5948-8fb4-5da66c443137-A  # ilbc
11c31109-22c4-539f-8f30-dcfe112c5668-A  # mlp
3dd82777-77f3-5dc6-a81e-2c208596dcf3-A  # mp2
9da4abe5-6e44-5610-9d4c-4a102948a655-A  # mp3
006b937d-4899-5edb-aa91-88d60febd3be-A  # nellymoser
8faa0976-d9cf-51f8-bff8-493348174707-A  # opus
a79b9884-cf03-58d8-a80a-b194af1e28d1-A  # pcm_alaw
7acfc416-58bd-50df-8a33-c3cd03ff91d0-A  # pcm_bluray
3535a1af-9081-5d23-94ec-4cafad112e55-A  # pcm_dvd
4cbb5323-3af8-5b50-88db-f55c69935180-A  # pcm_f32be
3138fb08-524d-5263-b0fa-2d8467104dfb-A  # pcm_f32le
7ba4281a-69d1-5e10-8766-fa1104e3ca76-A  # pcm_f64be
b5fb6bc9-e848-52be-b707-0e1feb9b8b52-A  # pcm_f64le
e812c6d9-fcff-576e-9713-1324cfeac63e-A  # pcm_mulaw
6514e33f-52af-5634-a807-dd7d58721757-A  # pcm_s16be
17a6250f-7479-5e72-9629-4337ea1e169b-A  # pcm_s16be_planar
b925925b-92a0-5b4e-9374-b2c6e27c1cef-A  # pcm_s16le
6e405ebc-da27-5563-9945-93854e2201a1-A  # pcm_s16le_planar
8db792ed-eba8-5bf6-8e45-66cd20106bb3-A  # pcm_s24be
cbff247d-ad97-55a2-9a3a-bbfd6db39a5d-A  # pcm_s24daud
76f5a80c-f320-528c-ab8a-e1b24202ee75-A  # pcm_s24le
6fde9a3a-33ef-513b-b3b4-0b936706c7fb-A  # pcm_s24le_planar
730bf178-ea1e-5919-9ce8-991d58aca1d2-A  # pcm_s32be
9f7149f5-3d6c-5039-9279-82c7f85c21d5-A  # pcm_s32le
76376c2b-007a-5124-b598-27b515dac507-A  # pcm_s32le_planar
4cb8d100-9c83-5e70-8aa6-93f4d96193e1-A  # pcm_s64be
d40c5eb6-85da-54b7-ae97-53ab24a49b42-A  # pcm_s64le
663e1bd7-20ac-56e7-a333-44539facf66e-A  # pcm_s8
4b015a86-6d75-59d3-aea9-316c6c6d6580-A  # pcm_s8_planar
b7a37796-c65c-5146-a189-316c3138268e-A  # pcm_u16be
1f3cf0d2-c7b8-5131-8a82-9f3134eb5535-A  # pcm_u16le
e0e15a8f-db5c-5689-9368-9e326dd5ec09-A  # pcm_u24be
4c309438-c681-5167-bf87-6404f8ffa4b1-A  # pcm_u24le
9afd411f-ed1e-5810-999c-0269d744983d-A  # pcm_u32be
3103cb65-d58d-52a3-8f13-ea18e9847950-A  # pcm_u32le
172ae5c5-f336-5f5a-90a5-a776168ca977-A  # pcm_u8
6a6cc0a6-55fa-577e-8be4-93510b6ee9d8-A  # pcm_vidc
688c6d5a-6a5d-5837-ba3e-57c3cd96b71c-A  # ra_144
c05d3129-91b8-5fe9-a121-cf964f4cc059-A  # roq_dpcm
043a0079-f71c-5f5b-8f33-b70d7c0c8f38-A  # s302m
e7f84648-1085-569d-9fd4-ec8b6be77364-A  # sbc
e5d98d48-dc0c-5ff1-acb0-78db35e9fd32-A  # speex
26282d63-a325-5f0a-9423-3cc70d5972f6-A  # truehd
9c62fa8b-d82f-5eaa-b862-21088cdb4091-A  # tta
acf1a687-3cf9-5ead-9656-b9d331a3f421-A  # vorbis
888a6208-e328-5238-bd10-6f4e56a381d3-A  # wavpack
7ffe2fb7-fd00-566d-be86-61fd54358384-A  # wmav1
5ee4140d-a6d0-53f7-bad0-2597e54097b4-A  # wmav2

# Image Formats
169ebedc-69b8-5a8e-ac64-df1a8eee5b92-I  # avif
808b7568-daf7-5b4a-959d-79e3f3765189-I  # gif
768db60f-4e74-52f5-a2dc-56060da83b8c-I  # heif
c416405f-af41-56cb-8c6c-46533f290969-I  # jxl
002b5a9f-6bbb-5c17-ab0e-f3abb791ab72-I  # webp

# Camera RAW Formats
facc476b-bc24-5e80-87a9-d54289a059c3-R  # arw
ac126046-11bb-5544-a3a7-27d6153bc432-R  # cr2
a829ec18-757e-5217-84de-48784fc699bb-R  # cr3
ae6404c9-613b-5ca4-9c5a-e30370fada54-R  # dng
16e292ec-83ed-55b2-b4ba-39f714afa804-R  # nef
b2f15c88-20f2-548c-b21e-2f0c520bd7da-R  # orf
8e2ac93c-d3f8-5d19-9bf8-3e5beeb3e404-R  # pef
a5e9f1bb-0f88-5549-b246-06793a1f350a-R  # r3d
a9997994-18d5-5fb2-b76b-6d12d242129d-R  # raf
c3fbb54e-1107-54a7-8123-2f1fad9b843d-R  # rw2
0283bda1-fa3f-5eea-b4bf-8530217aad6d-R  # srw

# Pixel Formats
f95cf84d-4328-533f-a8a9-5e6d8bace871-P  # 0bgr
85ea9e96-7570-5c6f-b70f-7f3a42bf0eeb-P  # 0rgb
4017c4f1-a629-5690-90b6-d9e5fa2d13c0-P  # abgr
d89888d0-db57-5374-bc77-9f390002682d-P  # amf
983e0b8f-8c93-532e-a0a2-65407dc8c453-P  # argb
9daf70d6-c6c1-56b8-ba8b-cc6ea66df756-P  # ayuv
a66439ef-9c88-50ad-a1e9-e90fdf144794-P  # ayuv64be
033ea2b2-00c9-57c3-b650-67216cc24fae-P  # ayuv64le
3882a9e2-e90f-5f12-8083-85994fa95cab-P  # bayer_bggr16be
d2b8c2cb-0359-5b94-98b0-205b65deebfa-P  # bayer_bggr16le
e53943fa-bf43-514f-9acd-d41c8cfa940a-P  # bayer_bggr8
282c893c-c3f5-56a6-9b36-08274a7fc8f0-P  # bayer_gbrg16be
65cd3f75-07ec-51d4-917a-9e85ab167ed3-P  # bayer_gbrg16le
774bb201-a1fa-5917-9636-1e03fb968b12-P  # bayer_gbrg8
af428b58-97e7-5de0-a411-e761bf507730-P  # bayer_grbg16be
2a4b6929-598c-59eb-869e-7e61a1527ff1-P  # bayer_grbg16le
abc405e2-1291-54cc-8b71-0535b5b01e2b-P  # bayer_grbg8
1b6022ce-ade2-5d2d-8042-935e64cb862e-P  # bayer_rggb16be
8e68b204-5204-507f-aff4-24f155863d0d-P  # bayer_rggb16le
af6879f7-6234-50af-a861-3ef215edbd2e-P  # bayer_rggb8
8c2b05ef-bc3d-5637-9134-5e080b4ad484-P  # bgr0
f0cf2e5f-4077-570d-8097-d560e0f17fcb-P  # bgr24
1c02a525-3f11-5ccb-86a1-f84dc131acf7-P  # bgr4
5f615d34-aed5-5a50-a402-537fd1ddaf36-P  # bgr444be
bd842e39-ab13-5110-a41a-5947b86515aa-P  # bgr444le
a3280f96-122f-5ab0-88a7-2486865580ab-P  # bgr48be
651b4a53-0050-5b3b-8bf9-5cb9c1ede9c2-P  # bgr48le
64a9a1e4-bc71-588c-9e2e-d239f726eb4f-P  # bgr4_byte
57ce6f2f-8d56-5908-af1c-34df22269869-P  # bgr555be
f61bf438-4b53-54c0-ad1d-2b25933ba8d5-P  # bgr555le
0f2d1686-fc74-5608-a618-3600f37e9ffb-P  # bgr565be
b65b8eac-a954-59f7-a65a-341682f5e1dc-P  # bgr565le
8140c928-f0a3-5364-8cc5-30031271e0a9-P  # bgr8
08fc966a-7cba-5a98-b019-359481f3f633-P  # bgra
bf383723-58d9-52b8-ac8c-897a58012734-P  # bgra64be
696dd3be-b0fc-57dc-aada-469e03af5649-P  # bgra64le
5adf8fde-a811-5a81-83c0-e7297e30eb61-P  # cuda
514ee48c-4abc-5121-b72e-556b083da451-P  # d3d11
8a96c9d1-2cda-5476-85a1-919068c13bff-P  # d3d11va_vld
29f4bc1c-2371-5cd9-9bcb-4f773d122115-P  # d3d12
6ed63d45-1c21-5856-a701-60a1a1aedd9f-P  # drm_prime
95902d5b-09d6-56ae-820d-b51f3b47d090-P  # dxva2_vld
80d21716-c680-5958-9ce0-b9c665967602-P  # gbrap
67c1f16b-dfce-5132-b576-8ea940f55ab6-P  # gbrap10be
fc708c80-d4d4-54e0-9a23-2b6b2024c692-P  # gbrap10le
6b3c5f30-e778-5ac7-9ded-a115e8f33a93-P  # gbrap12be
0517a731-bc92-5a23-b71d-00d0ea0b5d66-P  # gbrap12le
ee15ef3b-5405-51cd-95e5-489c84774df7-P  # gbrap14be
2ee14192-5538-59a6-bbed-17b7c49b94e1-P  # gbrap14le
2c466cab-7973-5669-b931-4e40e56d9492-P  # gbrap16be
39a67a31-bb7d-5d3b-abef-69adb9087866-P  # gbrap16le
317d613d-ae78-5620-8192-09403f7d02d2-P  # gbrap32be
906bc147-d002-54c9-8d22-a4592fe16673-P  # gbrap32le
b67bfaf9-72c8-5ed7-8aa2-ce83acfb746d-P  # gbrapf16be
8f6ff09c-ae2d-56a1-8e4c-fa37f463e545-P  # gbrapf16le
0bf56bda-04c0-56c4-a66d-a618879e4c35-P  # gbrapf32be
4ef3a109-c613-5015-8d48-22c903819dcd-P  # gbrapf32le
7e608415-23a9-59aa-ad5e-899e5aa55371-P  # gbrp
c25511c2-6b5e-5759-b15f-c33f085b600c-P  # gbrp10be
978bf145-de80-5142-89ae-896b308e5b0b-P  # gbrp10le
80169ad7-ed1b-5729-87a0-f53ed88f75f5-P  # gbrp10msbbe
a09df4d9-cfcb-5b8f-833d-d4366a9ad254-P  # gbrp10msble
139e40eb-a58b-5ee0-871f-a3df3cb2e06d-P  # gbrp12be
8df8d81f-dfe9-54a7-8e4d-addf99161e8e-P  # gbrp12le
c09bbe8b-3ba9-5048-96d8-00a91244cdba-P  # gbrp12msbbe
ce4d21d8-f15d-5a08-a3bb-e451f568d3d1-P  # gbrp12msble
afee8954-ad66-59d9-92a8-605725577b26-P  # gbrp14be
63b57793-8e54-527a-80a5-d2ca3ae7bc9d-P  # gbrp14le
ba916d9f-b2b6-582c-8feb-9ae36371d7c1-P  # gbrp16be
19f5877c-ca1b-5183-a6ed-023a6c3b4cff-P  # gbrp16le
647b0f34-0d9b-5116-99b9-de5d11a34950-P  # gbrp9be
a2fec621-9927-56b3-a519-1ae13cfa1c5b-P  # gbrp9le
88f6aa64-e0b0-5a08-a397-7e89878af574-P  # gbrpf16be
8cd0add7-3fa7-5da0-ab31-3c7256446afa-P  # gbrpf16le
413bf505-4291-53ee-ab24-e9948bded461-P  # gbrpf32be
7e2fd5b6-2acc-5ae3-ae5f-7277ed5e43e2-P  # gbrpf32le
0d724a1d-0313-5b4d-a309-43d248252cf5-P  # gray
67682a41-f174-5a3a-8979-cc94cc7f2564-P  # gray10be
05a0295c-2927-588f-bf0f-07fbf7d0f105-P  # gray10le
bcd816e4-136f-52cc-86ab-16d2e0e45515-P  # gray12be
5b31a2e9-37ba-50ef-add0-71b26efcab34-P  # gray12le
04985628-495e-5968-8fd4-d0b5b385b6c9-P  # gray14be
94cb6824-b532-53e2-a0a9-c6cb2f35b93a-P  # gray14le
59742286-26a7-5511-b287-81a8af0b65b6-P  # gray16be
f68ed970-c53b-5405-8772-ec83a0b50044-P  # gray16le
15f16d67-72b4-599f-a0cb-fedc81471977-P  # gray32be
1d23e8b2-8e8c-531d-92ad-3d7a3f0d54eb-P  # gray32le
86d34a18-8a47-53a9-a862-863a1ee5b835-P  # gray9be
f9f1b4ab-3fc4-57fb-a0e1-5d94813ca574-P  # gray9le
0a55d4ea-2500-5b34-8033-88d09266dd78-P  # grayf16be
5b825b0d-ce43-5b50-84ea-452a15048b5b-P  # grayf16le
e8d71899-cb9f-55c4-b0aa-8f730d6264f9-P  # grayf32be
9de73919-7c45-526f-bca7-34f2237fbd78-P  # grayf32le
eb3af5aa-e940-5c01-8131-da11c92efb73-P  # mediacodec
fcc233c0-8eed-52d7-ba9d-3a765c2e7d7f-P  # mmal
6e6faf58-e652-586e-bb7f-088160bc19a5-P  # monob
44645ee7-20ee-5363-898b-bf2e77cb0e42-P  # monow
c9f224a7-fbc8-5b18-8996-9121c59fa8ee-P  # nv12
a5bfb076-292d-517a-bdd5-140bd85518b7-P  # nv16
5414b907-ac3b-5754-809e-55e8475ac581-P  # nv20be
cf231a94-f18a-5fa3-aa31-575993eacffb-P  # nv20le
0ad88034-0fdf-5559-ac33-5e04ad3c1a44-P  # nv21
1a090ef5-8aaf-5803-a0ae-6db993a012da-P  # nv24
5bfe0e9c-81b6-551e-9169-5e6c6dc37d73-P  # nv42
64440173-922c-5937-b730-047ad6f9882a-P  # ohcodec
a781ae6b-9670-585c-970e-da7a2a1ad678-P  # opencl
3f7256ca-2973-5443-9913-b342a0f5349b-P  # p010be
42a6e6a3-1e21-5802-9c5e-2506e6c9593a-P  # p010le
2193eb19-0bf2-5a2f-8b59-a1cd3d920936-P  # p012be
36546a9d-8b5b-5a5c-9acd-9c66b9ba920e-P  # p012le
60c9d714-bb53-5ed9-ba3e-9c1641bb6a95-P  # p016be
3a03e0e1-d0db-5e7f-9f7b-d2ea2c878b06-P  # p016le
93389c17-9293-53ca-b5d1-ad979f53e9d9-P  # p210be
4e2ef0a1-b536-5ae3-9868-ca4649f6a09a-P  # p210le
7ff921ea-6f0a-518b-8684-d9d33a431a6a-P  # p212be
0757d257-6c4f-518e-8610-bd5664d66aa4-P  # p212le
af3f54a1-b3ea-5e77-827c-e7b4cbb8799b-P  # p216be
7f615899-a2e1-5ea7-b3eb-04d13d25e5b3-P  # p216le
9107adf9-8ae4-584d-bdb3-83e596359b21-P  # p410be
2ea29ab7-2efd-59e2-86b9-1b5eee911fb0-P  # p410le
cc966980-ce68-5c6a-be1a-d8dab3c4433a-P  # p412be
01b38f2b-fcad-5d35-b5c6-6263c1249924-P  # p412le
2a991239-c5c3-55fd-a11c-e0c1372db624-P  # p416be
35a845c3-c82a-5eec-b7f5-0848e3c1e276-P  # p416le
3f8e02e4-cb07-5704-8446-3b4ed13f9a08-P  # pal8
10ad569a-8d45-51df-959f-75e39d5296bd-P  # qsv
313958ff-a1b3-5cff-9bcf-204139a52eca-P  # rgb0
712d8952-caea-5ab1-a169-283a04c78b96-P  # rgb24
428e2a94-d9b9-5341-806c-9ba288ab9aff-P  # rgb4
58057add-c549-5ce4-8174-4dbe75f7c0d7-P  # rgb444be
a80db3b3-47d0-596b-b56b-57cc3bbf7e76-P  # rgb444le
2667c2b6-5f68-5ce8-82e1-2f58a8d696bc-P  # rgb48be
f1c75b25-f26a-528d-b644-7dfd07bf354f-P  # rgb48le
7212e45f-c79a-5b41-8f7e-98eb9e3a4231-P  # rgb4_byte
dd4c2ca8-cd86-5a8e-97e2-c44d98390105-P  # rgb555be
1e2068af-4566-550b-a933-c0c0be4ceb4e-P  # rgb555le
6826a7ac-77af-5f60-b2e3-392ebd596bdd-P  # rgb565be
eee93027-515e-5dff-9c70-fc186dc9b392-P  # rgb565le
e95a1704-18f7-5bec-98c3-ad0a7be451bf-P  # rgb8
016c28c8-9d61-5ee1-a612-a48f352da885-P  # rgb96be
eaabbf4b-a48a-5c48-979d-da2a3c04cf8d-P  # rgb96le
111373e7-386c-5b52-9956-e6f91e0574cc-P  # rgba
16d4df13-37a5-577c-b5e3-a712847f3127-P  # rgba128be
66d16e36-dce6-5dcd-a39b-2cd393afbdf1-P  # rgba128le
c7cbd325-fd58-5517-b812-05602c14c6f7-P  # rgba64be
3efc303d-d8f6-5cc4-a19b-083e606bbcc3-P  # rgba64le
c09bfca7-ea35-5335-be97-7a1532a034b3-P  # rgbaf16be
ec7bd932-a4ea-5634-9223-e28a483a3bdd-P  # rgbaf16le
d7d25682-ffd1-552b-a8e7-d661881f5ee5-P  # rgbaf32be
fbb26650-d51a-5d02-8daa-f8fa49411ef2-P  # rgbaf32le
108f4e73-0409-5e6f-a305-7ec57ad5a4a6-P  # rgbf16be
25c958c0-7e90-56fa-90cc-c7d3c2e37481-P  # rgbf16le
6a12dded-8653-583c-b612-ff06591023ad-P  # rgbf32be
9cc28f00-22db-561a-ace7-15394c8dff7d-P  # rgbf32le
f24e3288-ca57-5fd9-a37b-1cf6d2f5e27e-P  # uyva
18867a22-4ed8-5148-8e45-718b18237bb7-P  # uyvy422
85aff510-e516-5355-bc35-f7b996cbc285-P  # uyyvyy411
54d60651-0779-508c-a57f-0a7ba09aeed0-P  # v30xbe
28e1848e-6c89-54d4-a2b5-4d5a34416a1d-P  # v30xle
473b09dd-997a-50cb-ace1-66df5e0ce831-P  # vaapi
0b6ade1f-789a-50ba-9a16-a25dc8e5422a-P  # vdpau
e87ba2f5-7a5e-5f43-99ff-b7c64a0a2dd0-P  # videotoolbox_vld
01c0be8f-06c0-511e-b740-451b327a52b5-P  # vulkan
cfda7103-e3bc-53fa-b486-741846e6abd7-P  # vuya
9516bf72-794d-58e6-ae42-4b5c2f88ce02-P  # vuyx
497e1861-867f-5ff4-9915-0f6b41edadf3-P  # vyu444
0c60f06e-7728-5b74-98b8-b3f102a6de7d-P  # x2bgr10be
cc2e96bf-77cf-5048-903a-1f5409c61efd-P  # x2bgr10le
d57db321-8331-5137-8fc6-690c5bcd2746-P  # x2rgb10be
3fd69399-89e9-5cd9-af90-ab84225c244c-P  # x2rgb10le
e1ceff4a-b183-52be-920e-0a6c5defa9e9-P  # xv30be
2fc7c0ab-6501-56b5-b4e3-c1a4994d88e9-P  # xv30le
5ee9cf36-1539-5391-b401-d4208002d48e-P  # xv36be
111b0148-20bc-5725-9a1a-d77fefec5860-P  # xv36le
5469dee1-eec8-5b52-a34c-dda5a4cd40d3-P  # xv48be
a496f172-5bfb-5007-9574-eb6ab90c24ff-P  # xv48le
5ef2d866-7d90-58f1-8b34-73ee5d8b28ab-P  # xyz12be
a0a11385-cdbc-50a2-8e17-6c277fe3a39d-P  # xyz12le
4055f9d9-85c7-5a34-9271-ac35952399d1-P  # y210be
b4d24256-99a1-5af7-a189-a0b9eaee5e67-P  # y210le
b9a72358-9226-5610-befb-857e447444c2-P  # y212be
e9497060-fc08-5e6b-92f2-807b3c655990-P  # y212le
5f651508-2287-585e-bdfa-d170ff7db5b0-P  # y216be
1e8e52f5-f8b3-5bef-b677-173ff5fbb321-P  # y216le
d3abdf2c-9e39-5c7b-b9d4-cd2ba3e30cac-P  # ya16be
9794358f-5d54-5326-b0c3-c84718c4b6e2-P  # ya16le
bae63827-89ef-5d3d-b951-0a5cf9739285-P  # ya8
28f0518b-2e2c-53e0-a25a-2e1e7628ad1a-P  # yaf16be
55ba54ad-9a0c-5910-8b58-30465cb7bd8f-P  # yaf16le
84d0630e-cc96-5688-b497-6e4893414ce7-P  # yaf32be
728bc5fb-09cb-568b-941e-1751260a6035-P  # yaf32le
d2958ab9-4a6a-5450-91a0-3f6930a24a8d-P  # yuv410p
6cfda5d5-1ac0-5cf2-ae7d-c6b168bf5529-P  # yuv411p
7c724e5b-afb5-5ae2-a632-f29ea361a240-P  # yuv420p
989a5664-c736-5614-9b82-5ee9df80a3b1-P  # yuv420p10be
d269b27e-6746-5a9b-959d-4e24f77fcf36-P  # yuv420p10le
8833f09e-cb7f-5b21-ae4d-d5fff531f3f6-P  # yuv420p12be
9348ee7c-982a-5844-bf23-20ca736c85d6-P  # yuv420p12le
a6cdc23f-82a5-5f85-8d4e-a21f211a6b42-P  # yuv420p14be
50dd2b44-2663-506e-99c0-86951be37eb6-P  # yuv420p14le
60cef4dd-b8ca-547c-90f8-d29589bb7d30-P  # yuv420p16be
869975ea-b396-5e9b-9b31-c9fe8ad0367f-P  # yuv420p16le
5571e9c3-97fb-53e5-a444-69ba1ec05608-P  # yuv420p9be
4565bb5f-bc6c-551d-9373-a5c74560f05a-P  # yuv420p9le
ae166841-c950-5de9-892f-6646aff3e5fa-P  # yuv422p
3f604d42-bec7-5bad-82af-44c8d30309da-P  # yuv422p10be
4c74843e-8df8-5c4c-9bb0-9cf2e62b4f04-P  # yuv422p10le
d1baabae-b355-5c40-a3af-ae4b6bcd968c-P  # yuv422p12be
3f78a926-1f1f-5471-bf1b-983f20a344b3-P  # yuv422p12le
709ddd37-2e4d-5910-9bbf-6d590ada076c-P  # yuv422p14be
bf09ac73-23f3-513e-9a5e-8119e62ffb22-P  # yuv422p14le
3cc4b45e-6bb5-55fc-97d0-f69301816277-P  # yuv422p16be
c1056fd9-dca8-5088-81ff-b256dd52721d-P  # yuv422p16le
3ce6f699-4a77-55e9-9ba2-b15944357932-P  # yuv422p9be
c4bd15bf-6a48-5147-8fc2-fc5e7b471164-P  # yuv422p9le
cf1e3bb3-33ef-596e-9ede-644e8cd3cce2-P  # yuv440p
e727c9dc-cad7-53b2-85cc-903b5cc1e12f-P  # yuv440p10be
0564b7f6-1f73-5ef8-9de0-a3f5496dbbed-P  # yuv440p10le
7ab97f08-2e54-5d0d-bbc8-07b5eb760f3c-P  # yuv440p12be
d5e8adbc-6454-55d0-a908-941ce2247daf-P  # yuv440p12le
6698c78c-3390-58ae-bd28-01005ff8a945-P  # yuv444p
6277bad2-43d8-54f6-8be2-dde8aad8e767-P  # yuv444p10be
5acae7b9-28ec-563d-ae34-fe4401d47672-P  # yuv444p10le
992881d4-dd15-53b6-8c33-da7d95317cc2-P  # yuv444p10msbbe
4d0eeeff-893b-5fd2-8f8a-cc34f88ae56d-P  # yuv444p10msble
665f2d43-bbc7-51fe-8a58-bf606835cb30-P  # yuv444p12be
af039f23-684d-5870-87f7-e822b8c466be-P  # yuv444p12le
1379093d-6c1a-5484-aa4e-921419a9ddcc-P  # yuv444p12msbbe
d6f1afde-c782-531e-ade8-1e0774b05553-P  # yuv444p12msble
cf177923-3b6f-52b7-bd14-ed0e7d1fc8e1-P  # yuv444p14be
b17375d8-3277-5aa3-95fd-8ccdd3446c6a-P  # yuv444p14le
98492ffc-b180-51b7-be20-6ff5363ec489-P  # yuv444p16be
971ac667-1e6f-5c4d-a63c-6604b1850dc9-P  # yuv444p16le
093552a5-4e2b-5fd2-826c-d90194b9708e-P  # yuv444p9be
d84e76a0-d708-539a-b679-7d3be77018ea-P  # yuv444p9le
6ed1797b-ae67-5e03-a75f-d412fb31aa1d-P  # yuva420p
dca7b036-55ba-5c01-a85d-a625820858ad-P  # yuva420p10be
5b217950-63e5-5656-8c7e-d44036e0d704-P  # yuva420p10le
db7a347d-85fb-598a-88ec-958f1408f633-P  # yuva420p16be
9c4252de-08b8-5b52-b647-d4f3630282c3-P  # yuva420p16le
14b664f7-da41-5977-8ffd-b596cb17596a-P  # yuva420p9be
647f7a7e-59aa-5396-9770-0eca094b3252-P  # yuva420p9le
58ab0ed2-3ad2-57bb-966d-9f1b47413ee8-P  # yuva422p
83acd17a-91e6-531f-83ab-1a250b1ce33b-P  # yuva422p10be
c0b9d15f-0558-5717-9c2c-6bb47fc49788-P  # yuva422p10le
f792517f-a60d-5c11-8563-5fa909a8fe3f-P  # yuva422p12be
7885309e-db56-54f6-b49f-c08c562ca01c-P  # yuva422p12le
044ad9d2-765f-56a0-91e3-cba273286b76-P  # yuva422p16be
48dcc721-dd37-5c76-aed5-6431bd1e4bbe-P  # yuva422p16le
cfb1840b-3885-5f9d-8fc1-0fa75122adfb-P  # yuva422p9be
80131528-52a9-5884-8644-ba45d1343686-P  # yuva422p9le
37dd5de0-95f0-5dbb-b36d-247e6a3174f4-P  # yuva444p
ace10291-f37a-5352-9c1d-65f531ab8d85-P  # yuva444p10be
c460285e-3590-5e5c-885a-cf7f2a070b76-P  # yuva444p10le
ac9076e2-67c0-5520-bd12-35633323daed-P  # yuva444p12be
fb199e42-7d45-5618-b75a-a3977fb3351d-P  # yuva444p12le
380644ae-fac2-58ab-9383-623f083598e1-P  # yuva444p16be
68729143-d7c4-57e4-884e-7335eda09f67-P  # yuva444p16le
8e0a7235-8736-5502-87b0-23b9c7f8cbc6-P  # yuva444p9be
14f549af-57a9-5c9b-ad6b-2e54638b8dac-P  # yuva444p9le
675e4fb0-ba83-5ba4-82fd-6214d8c77ba8-P  # yuvj411p
cf17433d-4942-5c10-8f7c-9eedb6a9700e-P  # yuvj420p
df122b92-73d1-52ca-bdf6-10b778f4c12b-P  # yuvj422p
1684fd14-854c-53ea-b849-08de639cb5db-P  # yuvj440p
b77ea6ba-fad5-521d-beb7-71269c098c98-P  # yuvj444p
13842c35-7de1-523e-9f7e-0501fcb2c00e-P  # yuyv422
6334770d-8239-5be8-8a30-be534033d99d-P  # yvyu422

# Audio Sample Formats
0f05e3cb-47cd-52a6-9c27-d2c24f50754c-S  # dbl
a9e29bfc-2824-58e8-8762-ef6783b33068-S  # dblp
a54d0973-258b-55a4-bbed-ecca449db7aa-S  # flt
5dce2525-7000-5cb1-b102-8f4bec8bdff5-S  # fltp
d82de5f7-a7b9-5b3e-b763-9abd6b1967e4-S  # s16
9e2f723b-1702-53b5-ba40-bcab3ea4a612-S  # s16p
31b6ad94-26ba-50a3-8e1a-bc84df737298-S  # s32
f85ac22b-6e80-5a5f-96e3-7a19d77ad750-S  # s32p
eae29e63-414b-5852-9216-edc7c34a7299-S  # s64
28480542-3a80-5b0f-9e6d-9cde1d856970-S  # s64p
79a0938d-feee-54e1-8267-12688fe3f683-S  # u8
fb8a3408-3c8a-5c3b-937d-ccd7740f571b-S  # u8p

# Audio Channel Layouts
9f0b415a-a3b2-524e-9be0-289d1833ee21-L  # 2.1
b85b3b9f-5fe2-55fc-b762-c7643a66e1b1-L  # 22.2
03fa9289-db23-5422-9731-c537a575f4f3-L  # 3.0
069e56e7-3359-5861-a25d-fe5c13f20dd0-L  # 3.0(back)
5e84d5b4-9f95-5e35-968b-338b63baa970-L  # 3.1
e2dadd02-1792-5ec3-946e-0ca5ab79d4da-L  # 3.1.2
1c0266a4-ca59-5c5f-9912-4f5b6321e1d8-L  # 4.0
b3012f1e-0791-5d28-9158-f217d2a448ac-L  # 4.1
802ecc25-c59e-5cb1-951c-55dab478fcae-L  # 5.0
9a38ce29-8a30-563e-afca-1c2f18acf651-L  # 5.0(side)
0f74c57c-2396-5fc4-825e-6e11bb400e98-L  # 5.1
69597858-d182-5f3a-9dc5-99853f8f46dc-L  # 5.1(side)
74301fdb-5f55-5bde-b06b-9316370d93dd-L  # 5.1.2
2dee444e-02bb-50fd-a55e-ff69e6d438f5-L  # 5.1.2(back)
ba4d56a3-312f-59db-b1c5-cf6568c280d6-L  # 5.1.4
b1a67332-dccc-5cbd-8b5b-51ad64a4bbed-L  # 6.0
9994a054-0503-5c22-be1a-47942e510af6-L  # 6.0(front)
683efc40-02eb-5a2a-a932-44f26c5e8f86-L  # 6.1
37d01fd9-d2e4-5e7a-984d-4245e0e2bd2a-L  # 6.1(back)
641d67da-2d36-5b1b-a3d1-6945d90f7005-L  # 6.1(front)
ff97c52e-43a8-5e2b-a11b-f49faff24bab-L  # 7.0
3f39ab23-8237-5af8-8bc6-3fa45b3bedae-L  # 7.0(front)
9e1b4b6e-ade7-56a0-a992-68cb4dd838d6-L  # 7.1
cc1a0e0e-8f7f-5e6c-8937-9425fea100f0-L  # 7.1(wide)
0d3ad488-3968-5127-ab29-45dc52665f59-L  # 7.1(wide-side)
82d3d25d-cd72-53fe-8781-1391a070c122-L  # 7.1.2
a3ab12ca-4319-51e4-91fd-fd5b1cc9353d-L  # 7.1.4
f475b83f-021a-51fc-8fb2-2707c15486bc-L  # 7.2.3
d777844a-7feb-500c-8373-0de481ffb420-L  # 9.1.4
2fbf2db7-a6e0-5618-bcc7-5f6ba738d139-L  # 9.1.6
09899e01-91f5-5164-bf4d-38d000a71c27-L  # binaural
171302fe-3ab6-5895-a3bb-8fc74fda4c9f-L  # cube
5a88dc9c-b51f-5171-837a-0a26cdab05b2-L  # downmix
10b22873-e538-56f0-a0e4-faa84d231e68-L  # hexadecagonal
0627cfbb-3caf-598c-ac4f-5ca22214ef19-L  # hexagonal
99799511-2983-5c0d-b1e8-41a5af0348eb-L  # mono
bdcfb498-95e0-5167-abf0-941f9a5a30e9-L  # octagonal
9ef0ea6b-c88e-59f3-8491-7e3c150200f4-L  # quad
4bf0d2b7-65b0-548d-b49a-44e2d2ee11d3-L  # quad(side)
8e57bfa8-40de-5f03-adc9-c7a858058d8f-L  # stereo
```

## Usage Notes

### For Developers

When implementing format detection:

1. **Query multiple tools** to get different names for the same format
2. **Look up the UUID** using any tool's output name
3. **Use the canonical name** internally for consistency
4. **Map back to tool-specific names** when needed for external commands

### Empty Fields

- **N/A**: Tool does not support this format category (e.g., Pillow doesn't process video codecs)
- **Empty**: Mapping not yet discovered (needs investigation)

### Extending the Registry

To add new formats:

1. Run format discovery: `python3 scripts/ultimate_format_test.py --skip-install`
2. Update `scripts/extra_formats.txt` with missing formats
3. Regenerate registry: `python3 scripts/generate_format_registry.py`
4. Manually verify tool-specific mappings
5. Test with actual media files

### UUID Generation

UUIDs are generated using UUID5 (SHA-1 hash) with:
- Namespace: `12345678-1234-5678-1234-567812345678`
- Name: `{category}:{canonical_name}` (e.g., `video_codec:h264`)

This ensures UUIDs are:
- **Deterministic**: Same input always produces same UUID
- **Unique**: Different formats have different UUIDs
- **Reproducible**: Can regenerate identical UUIDs across systems

---

*Generated by `scripts/generate_format_registry.py`*
*Last updated: 1761759480.86548*
