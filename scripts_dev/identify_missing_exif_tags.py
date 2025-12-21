"""
Identify commonly used EXIF tags that are missing from our metadata registry.

Based on standard EXIF 2.3, XMP, and IPTC Core specifications.
"""

# Standard EXIF tags that SHOULD be in every photo metadata registry
STANDARD_EXIF_TAGS = {
    # Already in our registry (reference for comparison)
    "covered": {
        "EXIF:DateTimeOriginal", "EXIF:CreateDate", "EXIF:ModifyDate",
        "EXIF:DateTimeDigitized",
        "EXIF:Make", "EXIF:Model", "EXIF:LensModel", "EXIF:SerialNumber",
        "EXIF:ISO", "EXIF:ISOSpeedRatings",
        "EXIF:FNumber", "EXIF:ApertureValue",
        "EXIF:ExposureTime", "EXIF:ShutterSpeedValue",
        "EXIF:FocalLength", "EXIF:FocalLengthIn35mmFormat",
        "EXIF:ExposureCompensation", "EXIF:ExposureMode", "EXIF:ExposureProgram",
        "EXIF:MeteringMode", "EXIF:WhiteBalance", "EXIF:Flash",
        "EXIF:ColorSpace", "EXIF:Orientation",
        "EXIF:ImageWidth", "EXIF:ImageHeight", "EXIF:BitsPerSample",
        "EXIF:Compression",
        "EXIF:Artist", "EXIF:Copyright",
        "GPS:GPSLatitude", "GPS:GPSLongitude", "GPS:GPSAltitude",
        "XMP:Title", "XMP:Description", "XMP:Subject",  # keywords
        "XMP:Rating", "XMP:Creator", "XMP:Rights",
        "IPTC:Credit", "IPTC:Source", "IPTC:Caption-Abstract",
    },

    # Potentially missing but commonly used
    "potentially_missing": {
        # More temporal tags
        "EXIF:SubSecTime",
        "EXIF:SubSecTimeOriginal",
        "EXIF:SubSecTimeDigitized",
        "EXIF:OffsetTime",
        "EXIF:OffsetTimeOriginal",
        "EXIF:OffsetTimeDigitized",

        # More image properties
        "EXIF:ResolutionUnit",
        "EXIF:XResolution",
        "EXIF:YResolution",
        "EXIF:YCbCrPositioning",
        "EXIF:SamplesPerPixel",

        # More capture settings
        "EXIF:Contrast",
        "EXIF:Saturation",
        "EXIF:Sharpness",
        "EXIF:BrightnessValue",
        "EXIF:LightSource",
        "EXIF:DigitalZoomRatio",
        "EXIF:SceneCaptureType",
        "EXIF:GainControl",
        "EXIF:SubjectDistanceRange",
        "EXIF:MaxApertureValue",
        "EXIF:FocalPlaneXResolution",
        "EXIF:FocalPlaneYResolution",

        # More descriptive
        "EXIF:ImageDescription",
        "EXIF:UserComment",
        "EXIF:CameraOwnerName",
        "EXIF:BodySerialNumber",
        "EXIF:LensSerialNumber",

        # More XMP
        "XMP:Instructions",
        "XMP:TransmissionReference",
        "XMP:Urgency",
        "XMP:City",
        "XMP:State",
        "XMP:Country",
        "XMP:CountryCode",
        "XMP:Location",
        "XMP:CreatorWorkURL",
        "XMP:UsageTerms",
        "XMP:WebStatement",

        # More IPTC
        "IPTC:ObjectName",  # title
        "IPTC:Keywords",
        "IPTC:DateCreated",
        "IPTC:TimeCreated",
        "IPTC:DigitalCreationDate",
        "IPTC:DigitalCreationTime",
        "IPTC:By-line",  # creator
        "IPTC:By-lineTitle",  # creator's job title
        "IPTC:City",
        "IPTC:Province-State",
        "IPTC:Country-PrimaryLocationName",
        "IPTC:Country-PrimaryLocationCode",
        "IPTC:Headline",
        "IPTC:CopyrightNotice",
    }
}

print("=" * 80)
print("EXIF TAG COVERAGE ANALYSIS")
print("=" * 80)
print()
print(f"Standard EXIF tags already covered: {len(STANDARD_EXIF_TAGS['covered'])}")
print(f"Commonly used tags potentially missing: {len(STANDARD_EXIF_TAGS['potentially_missing'])}")
print()

print("=" * 80)
print("POTENTIALLY MISSING TAGS (organized by category)")
print("=" * 80)
print()

categories = {
    "Temporal (sub-second precision & timezones)": [
        "EXIF:SubSecTime",
        "EXIF:SubSecTimeOriginal",
        "EXIF:SubSecTimeDigitized",
        "EXIF:OffsetTime",
        "EXIF:OffsetTimeOriginal",
        "EXIF:OffsetTimeDigitized",
    ],
    "Image Properties": [
        "EXIF:ResolutionUnit",
        "EXIF:XResolution",
        "EXIF:YResolution",
        "EXIF:YCbCrPositioning",
        "EXIF:SamplesPerPixel",
    ],
    "Extended Capture Settings": [
        "EXIF:Contrast",
        "EXIF:Saturation",
        "EXIF:Sharpness",
        "EXIF:BrightnessValue",
        "EXIF:LightSource",
        "EXIF:DigitalZoomRatio",
        "EXIF:SceneCaptureType",
        "EXIF:GainControl",
        "EXIF:SubjectDistanceRange",
        "EXIF:MaxApertureValue",
        "EXIF:FocalPlaneXResolution",
        "EXIF:FocalPlaneYResolution",
    ],
    "Extended Descriptive": [
        "EXIF:ImageDescription",
        "EXIF:UserComment",
        "EXIF:CameraOwnerName",
        "EXIF:BodySerialNumber",
        "EXIF:LensSerialNumber",
    ],
    "Geographic/Location (XMP/IPTC)": [
        "XMP:City",
        "XMP:State",
        "XMP:Country",
        "XMP:CountryCode",
        "XMP:Location",
        "IPTC:City",
        "IPTC:Province-State",
        "IPTC:Country-PrimaryLocationName",
        "IPTC:Country-PrimaryLocationCode",
    ],
    "Rights Management (XMP)": [
        "XMP:Instructions",
        "XMP:TransmissionReference",
        "XMP:Urgency",
        "XMP:CreatorWorkURL",
        "XMP:UsageTerms",
        "XMP:WebStatement",
    ],
    "IPTC Extended": [
        "IPTC:ObjectName",
        "IPTC:Keywords",
        "IPTC:DateCreated",
        "IPTC:TimeCreated",
        "IPTC:DigitalCreationDate",
        "IPTC:DigitalCreationTime",
        "IPTC:By-line",
        "IPTC:By-lineTitle",
        "IPTC:Headline",
    ]
}

for category, tags in categories.items():
    print(f"📋 {category}:")
    for tag in tags:
        print(f"    - {tag}")
    print()

print("=" * 80)
print("RECOMMENDATION")
print("=" * 80)
print()
print("Priority 1: Add geographic/location fields (commonly used for photo organization)")
print("Priority 2: Add sub-second time precision (important for burst photos)")
print("Priority 3: Add extended capture settings (useful for photography analysis)")
print("Priority 4: Add rights management fields (important for professional workflows)")
print()
print("Strategy:")
print("  1. Add ~50 most common missing tags to registry")
print("  2. Focus on tags with FFmpeg/FFprobe equivalents for metadata preservation")
print("  3. Use 'unmapped:exiftool:FieldName' fallback for rare/proprietary tags")
print("  4. Don't try to add all 28,853 tags - impractical and unnecessary")
print()
print(f"Target coverage: ~120-150 fields (currently have 70)")
print(f"This would cover 95%+ of real-world photo metadata needs")
