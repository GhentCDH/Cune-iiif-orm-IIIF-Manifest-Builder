# Cune-iiif-orm-IIIF-Manifest-Builder

## Overview

This project builds IIIF Presentation 3.0 manifests for the Cune-iiif-project. The manifests support multiple image layers, sign-level annotations, translations, transliterations, links to externa data etc.

## Table of Contents
- [Cune-iiif-orm-IIIF-Manifest-Builder](#cune-iiif-orm-iiif-manifest-builder)
  - [Overview](#overview)
  - [Table of Contents](#table-of-contents)
  - [IIIF Manifest structure](#iiif-manifest-structure)
    - [Tablet images](#tablet-images)
      - [Example](#example)
    - [Layer presets](#layer-presets)
      - [Expected Viewer Behavior](#expected-viewer-behavior)
      - [Important](#important)
    - [Sign Snnotations](#sign-snnotations)
      - [Example](#example-1)
    - [Translations](#translations)
      - [Example](#example-2)
    - [Transliterations](#transliterations)
      - [Example](#example-3)
    - [Links to external data](#links-to-external-data)
      - [Example](#example-4)

## IIIF Manifest structure

### Tablet images

For each tablet in the Cune-iiif-orm corpus, multiple images are available. Each image set contains 11 images displaying the tablet in varying lighting and color settings:
- 5 color variants
- 4 shaded variants
- 2 sketched variants

To allow users to select which image to display, the images are added to the IIIF manifest using the **Choice** pattern (see [IIIF Cookbook Recipe 0033](https://iiif.io/api/cookbook/recipe/0033-choice/)).

**Structure:**
* Each manifest contains one Canvas
* Each Canvas has an `AnnotationPage` containing a single annotation with `painting` motivation
* The painting Annotation's body is of type `Choice`, containing all 11 image variants as options
* Each image in the Choice includes a `label` property to identify the variant (e.g., "Color A", "Shaded B")

#### Example

Below is an example of how a Choice of 2 images is implemented in the Cune-iiif-orm manifests.

```json
{
    "@context": "http://iiif.io/api/presentation/3/context.json",
    "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222",
    "type": "Manifest",
    "label": {
        "en": [
            "O.0222"
        ]
    },
    "items": [
        {
            "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/canvas/0001",
            "type": "Canvas",
            "label": {
                "en": [
                    "O.0222"
                ]
            },
            "height": 6670,
            "width": 2945,
            "items": [
                {
                    "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/canvas/0001/annotation-page/layers",
                    "type": "AnnotationPage",
                    "items": [
                        {
                            "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/canvas/0001/annotation/layers",
                            "type": "Annotation",
                            "motivation": "painting",
                            "body": {
                                "type": "Choice",
                                "items": [
                                    {
                                        "id": "https://iiif.ghentcdh.ugent.be/iiif/images/cune-iiif-orm:testset:O.0222:O.0222_ColorA/full/full/0/default.jpg",
                                        "type": "Image",
                                        "height": 6670,
                                        "width": 2945,
                                        "service": [
                                            {
                                                "id": "https://iiif.ghentcdh.ugent.be/iiif/images/cune-iiif-orm:testset:O.0222:O.0222_ColorA",
                                                "type": "ImageService2",
                                                "profile": "level2"
                                            }
                                        ],
                                        "format": "image/jpeg",
                                        "label": {
                                            "en": [
                                                "Color A"
                                            ]
                                        }
                                    },
                                    {
                                        "id": "https://iiif.ghentcdh.ugent.be/iiif/images/cune-iiif-orm:testset:O.0222:O.0222_ColorB/full/full/0/default.jpg",
                                        "type": "Image",
                                        "height": 6670,
                                        "width": 2945,
                                        "service": [
                                            {
                                                "id": "https://iiif.ghentcdh.ugent.be/iiif/images/cune-iiif-orm:testset:O.0222:O.0222_ColorB",
                                                "type": "ImageService2",
                                                "profile": "level2"
                                            }
                                        ],
                                        "format": "image/jpeg",
                                        "label": {
                                            "en": [
                                                "Color B"
                                            ]
                                        }
                                    }
                                ]
                            },
                            "target": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/canvas/0001"
                        }
                    ]
                }
            ]
        }
    ]
}                                    
```

### Layer presets

Layer presets are modelled as W3C Web Annotations. Each annotation has the following properties:

```
{
  "id": "https://example.org/anno/preset1",
  "type": "Annotation",
  "motivation": "supplementing",
  "body": {
    "type": "LayerPreset",
    "format": "application/json",
    "label": { "en": ["High contrast preset"] },
    "value": [
        {
            "id": "image_id_1",
            "opacity": 1.0
        },
        {
            "id": "image_id_2",
            "opacity": 0.5
        },
        {
            "id": "image_id_3",
            "opacity": 0.1
        }
    }
  ],
  "target": "https://example.org/canvas1"
}
```

For multiple presets, create separate annotations.

#### Expected Viewer Behavior

When a users selects a preset:
- layers part of the preset should be enabled with the configured opacity
- Layers not part of the preset should be hidden.

#### Important

This LayerPreset structure is not part of the official IIIF Presentation API specification. It represents a custom extension using the flexibility provided by the Web Annotation model.

While this approach follows IIIF conventions and best practices, it will only be recognized and interpreted by viewers that have been specifically developed or configured to support this custom annotation type. Standard IIIF viewers will typically ignore annotations with unrecognized body types, ensuring backward compatibility.


### Sign Snnotations

The annotations are modeled as W3C annotations. Each annotation has the following properties: 

* **id**: A unique URL identifying the annotation
* **motivation**: Set to "describing" to indicate the annotation describes the target
* **body**: Contains two elements:
  * A **TextualBody** with the ATF transliteration of the marked sign
    * `purpose`: "transliteration" (indicates this is a transliteration)
    * `value`: The transliterated sign text
    * `format`: "text/plain"
  * A **SignPosition** object (custom type) describing the position of the sign within the text structure:
    * `side`: The tablet face (e.g., "obverse", "reverse")
    * `lineIndex`: Line number, 1-based
    * `wordIndex`: Word position on the line, 1-based
    * `charIndex`: Character position within the word, 1-based
* **target**: Identifies the region on the canvas
  * `source`: The Canvas ID
  * `selector`: An **SvgSelector** containing an SVG path that outlines the sign boundaries on the image


#### Example

```json
{
    "@context": "http://iiif.io/api/presentation/3/context.json",
    "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/anno-page/O.0222-signs.json",
    "type": "AnnotationPage",
    "label": {
        "en": [
            "Sign Annotations"
        ]
    },
    "items": [
        {
            "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/annotation/23b52153-2d3f-460a-8c4e-4950aa3e52f4.json",
            "type": "Annotation",
            "motivation": "describing",
            "body": [
                {
                    "type": "TextualBody",
                    "purpose": "transliterating",
                    "value": "5/6(disz)",
                    "format": "text/plain"
                },
                {
                    "type": "SignPosition",
                    "side": "obverse",
                    "lineIndex": 1,
                    "wordIndex": 1,
                    "charIndex": 1
                }
            ],
            "target": [
                {
                    "type": "SpecificResource",
                    "source": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/canvas/0001",
                    "selector": {
                        "type": "SvgSelector",
                        "value": "<svg><path d=\"M1087.50,931.70 873.10,916.65 884.35,1063.27 876.96,1162.99 913.89,1220.01 1037.62,1199.47 1135.50,1114.75 1083.79,1042.73z\" /></svg>"
                    }
                }
            ]
        },
        {
            "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/annotation/d29f0312-0523-46ff-9638-bdec764fbf94",
            "type": "Annotation",
            "motivation": "describing",
            "body": [
                {
                    "type": "TextualBody",
                    "purpose": "transliterating",
                    "value": "SAR",
                    "format": "text/plain"
                },
                {
                    "type": "SignPosition",
                    "side": "obverse",
                    "lineIndex": 1,
                    "wordIndex": 1,
                    "charIndex": 2
                }
            ],
            "target": [
                {
                    "type": "SpecificResource",
                    "source": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/canvas/0001",
                    "selector": {
                        "type": "SvgSelector",
                        "value": "<svg><path d=\"M1409.12,896.48 1385.22,982.57 1413.70,1012.21 1363.84,1106.39 1326.91,1121.16 1284.66,1097.16 1214.73,1087.92 1140.86,1076.84 1155.64,934.65 1205.50,862.85 1297.83,855.69z\" /></svg>"
                    }
                }
            ]
        }
    ]
}
```

### Translations

The translations are modeled as W3C Web Annotations. 

Each annotation has a body of type **TextualBody** with:
* `purpose`: "translating" (following W3C Web Annotation standard)
* `value`: The English translation text
* `format`: "text/plain"

The target is the entire canvas (no selector), since translations apply to the whole tablet rather than specific regions.

#### Example

```json
{
    "@context": "http://iiif.io/api/presentation/3/context.json",
    "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/annotation-page/O.0222-translations.json",
    "type": "AnnotationPage",
    "label": {
        "en": [
            "Translations"
        ]
    },
    "items": [
        {
            "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/annotation/O.0222-translation.json",
            "type": "Annotation",
            "motivation": "describing",
            "body": [
                {
                    "type": "TextualBody",
                    "purpose": "translating",
                    "value": "Five-sixth of a sar (c. 30 m2) and 15 \u0161e (495 cm2) of built house and uncultivated land. It is adjacent to the house of X-ili\u0161u and Ri\u0161-ilum. Its front lies against the public square, its back lies against that of the house of X. Nanaya-\u0161arrat and Igmil-Sin bought it from Sin-remeni son of Enlil-isu. They paid its full price of 10 shekel (c. 83 grams) silver. The transaction can never be disputed. They swore on the name of Lugal-Marad and Sumu-num\u1e2bim. Witnesses: Nabi-ili\u0161u his brother, Awil-Ilim son of Qaranum, Samiya son of Qaranum, Ur-narkabtim son og Ibni-X, \u0160ama\u0161-bani son of Ibni-X, Butram-ili and Ipiq-Ea son of X. On the 10th month\u2026 the nth year of Sumu-num\u1e2bim. Seal: Sin-remeni son of Enlil-isu.",
                    "format": "text/plain"
                }
            ],
            "target": [
                "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/canvas/0001"
            ]
        }
    ]
}
```

### Transliterations

The translations are modeled as W3C annotations. 

Each annotation has a body of type **TextualBody** with:
* `purpose`: "transliterating"
* `value`: The complete ATF (ASCII Transliteration Format) text
* `format`: "text/x-atf" (unofficial MIME type for ATF format)

#### Example

```json
{
    "@context": "http://iiif.io/api/presentation/3/context.json",
    "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/annotation-page/O.0222-transliterations.json",
    "type": "AnnotationPage",
    "label": {
        "en": [
            "Transliterations"
        ]
    },
    "items": [
        {
            "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/annotation/O.0222-transliteration.json",
            "type": "Annotation",
            "motivation": "describing",
            "body": [
                {
                    "type": "TextualBody",
                    "purpose": "transliterating",
                    "value": "@tablet\n@obverse\n1. 5/6(disz) SAR 1(u) 5(disz) SZE E2 DU3#.[A] \n2. u3 KI.GAL2.LA \n3. DA E2 {I}SZESZ?-i3-li2-szu \n4. u3 DA ri-isz-DINGIR \n5. SAG.BI.<1(disz).KAM> SILA.DAGAL\n6. SAG.BI.2(disz).KAM E2? is-si?-na \n7. KI {d}EN.ZU-re-me-ni; DUMU {d}EN.LIL2-i-su \n8. {I}{d}na-na-a-szar-ra-at \n9. u3 ig-mi-il-{d}EN.ZU \n@reverse\n1. [IN.SZI.SA10] \n2. SZAM2#.-[TIL.LA.BI.SZE3] \n3. 1(u) GIN2# KU3#.BABBAR# [IN.NA.LA2] \n4. U4.KUR2.SZE3 INIM NU.[GA2.GA2] \n5. MU {d}LUGAL.MAR2.DA \n6. u3# su#-mu-nu-um-hi-im \n7. IN.PA3(|IGI.RU|).DE3.ESZ \n8. IGI na-bi-i3-li2-szu SZESZ.A.NI \n9. IGI a-wi-il-DINGIR DUMU qa2-ra-nu-um \n10. IGI sa-mi-ia DUMU qa2-ra-nu-um \n11. IGI ur#-{gisz}GIGIR DUMU ib-ni-ki?-a-ab\n12. IGI {d}UTU-ba-ni DUMU ib-ni-ki?-a-ab\n@top\n1. IGI# bu-ut-ra-am-i3-li2\n2. IGI i-pi2-iq-e2-a# DUMU# [\u2026] \n3. ITI AB.<BA>.E3#(|UD#.[DU]|) [...] \n@left\n1. MU BA.AN.DU8.DU8# [KU3.BABBAR E2-{d}nu-musz-da MU.NA.DIM2] \n@seal 1\n1. {d}EN.ZU#-re-me-ni \n2. DUMU {d}EN.LIL2-i-su",
                    "format": "text/x-atf"
                }
            ],
            "target": [
                "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/canvas/0001"
            ]
        }
    ]
}
```

### Links to external data

The `seeAlso` property provides links to machine-readable data exports in various formats. Each linked resource is defined as a `Dataset` with:

* **id**: Direct URL to the downloadable file
* **type**: "Dataset"
* **label**: Human-readable description of the content
* **format**: MIME type indicating the file format
* **profile**: Reference to the IIIF Presentation API 3.0 seeAlso specification

This allows programmatic access to the tablet's transliteration, translation, and metadata in their original formats, supporting both human consumption and automated processing.

#### Example

```json
    "seeAlso": [
        {
            "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/O.0222-transliteration-atf.txt",
            "type": "Dataset",
            "label": {
                "en": [
                    "Transliteration (ATF)"
                ]
            },
            "format": "text/x-atf",
            "profile": "https://iiif.io/api/presentation/3/seeAlso.json"
        },
        {
            "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/O.0222-translation.txt",
            "type": "Dataset",
            "label": {
                "en": [
                    "Translation"
                ]
            },
            "format": "text/plain",
            "profile": "https://iiif.io/api/presentation/3/seeAlso.json"
        },
        {
            "id": "https://iiif.ghentcdh.ugent.be/iiif/manifests/cune-iiif-orm:sde:O.0222/O.0222-data.json",
            "type": "Dataset",
            "label": {
                "en": [
                    "Metadata"
                ]
            },
            "format": "application/json",
            "profile": "https://iiif.io/api/presentation/3/seeAlso.json"
        }
    ],
```

## Credits

Development by [Ghent Centre for Digital Humanities - Ghent University](https://www.ghentcdh.ugent.be/). Funded by the [GhentCDH research projects](https://www.ghentcdh.ugent.be/projects).

<img src="https://www.ghentcdh.ugent.be/ghentcdh_logo_blue_text_transparent_bg_landscape.svg" alt="Landscape" width="500">
