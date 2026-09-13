# Hong Kong activity and night lighting

GPT-6 Astra · research and implementation checked 6 September 2026.

## Area evidence and modelling decisions

These sources establish examples of neighbourhood and building use. They do not
measure which windows are lit or prove a single closing time for a whole district.
Older planning announcements provide context, not a current zoning certification.

| Area | Source evidence | Lighting interpretation |
| --- | --- | --- |
| Central | [Planning Department, 2016](https://www.info.gov.hk/gia/general/201611/11/P2016111100247p.htm) describes the commercial/civic core. [IFC's operator](https://ifc.com.hk/en/office/one-two-ifc/) identifies One and Two IFC as offices. | Office façades wind down earlier; mall forms use retail hours. Nearby mapped homes keep their residential profile. |
| Causeway Bay | [Hysan Place](https://www.hysan.com.hk/portfolio/hysan-place/) combines 15 office floors with 17 retail floors. [Lee Gardens](https://www.leegardens.com.hk/eng/about.aspx) lists Hysan Place shopping hours of 10:00–22:00 Sunday–Thursday and 10:00–23:00 Friday/Saturday/public-holiday eves. | Hysan's lower forms follow retail hours while its upper office windows dim earlier. The model uses one general retail curve; weekday-specific hours are future work. |
| Quarry Bay / Taikoo | [Taikoo Place](https://www.swireproperties.com/en/portfolio/current-developments/taikoo-place-and-cityplaza/taikoo-place/) is an office-led development with dining and other uses. [Taikoo Shing](https://www.swireproperties.com/en/portfolio/past-developments/taikoo-shing/) is a residential estate of 61 towers. | Adjacent office and residential clusters should behave differently. Building tags and land-use polygons choose their profile, rather than assigning all of eastern Hong Kong Island one use. |
| Mong Kok | [Planning Department, 2023](https://www.info.gov.hk/gia/general/202306/09/P2023060900290p.htm) describes residential and commercial development and mixed-use character streets. | Retain homes, shops and offices within the same neighbourhood. The mapped Langham Place mall uses retail hours; its tower inherits the parent office tag. |
| Kwun Tong / Kowloon East | [Planning Department, 2018](https://www.info.gov.hk/gia/general/201811/09/P2018110900248.htm) distinguishes the business area southwest of Kwun Tong Road from residential uses to its northeast. | Spatial land use helps separate business and residential areas when a building has no specific use tag. Industrial buildings use the daytime-work profile as an estimate. |
| Tung Chung | [CEDD](https://www.cedd.gov.hk/eng/about-us/achievements/land/regional-development/l1-tung-chung-new-town/index.html) describes a new town with residential and commercial development. [Citygate Outlets](https://www.citygateoutlets.com.hk/en/about/) lists daily 10:00–22:00 business hours. | Homes become brighter as the evening progresses. Citygate mall forms follow retail hours, while mapped One Citygate offices dim earlier. |
| Discovery Bay | [The developer](https://scadmin.hkri.com/en/Our-Businesses/Hong-Kong/Discovery-Bay) describes a residential community with supporting facilities. | Residential tags and mapped residential land dominate; specific shops/hotels retain their own use. |

The [DON DON DONKI store directory](https://www.dondondonki.com/hk/) also lists
24-hour branches: retail is not universally dark after midnight. A building
explicitly mapped as a 24/7 shop follows the overnight profile. Hotels, hospitals
and similar mapped uses keep a larger overnight light reserve. This is not a
complete survey of night businesses or a store-by-store opening-hours importer.

## Initial reproducible classification

The counts below describe the initial 42,892-form lighting study. The current
whole-territory build extends the same method to 117,062 forms; updated counts
and coverage are in [GEOGRAPHY-COVERAGE.md](../GEOGRAPHY-COVERAGE.md).

`city/data/activity.json` is a separate layer joined by the immutable building
form UID. It covers all 42,892 current forms without changing any footprint,
height or district coverage. Building forms include individual parts of one
physical building.

1. Apply the two explicitly sourced mixed-use corrections in
   `source-scripts/city/activity-overrides.json`.
2. Read retained OSM current-use, building-part, amenity/tourism, shop, office and
   building-type tags; consult the parent if the part's use is unspecified.
3. Otherwise choose the smallest relevant mapped land-use polygon that covers at
   least half the building footprint. This is labelled an **estimate**.
4. Retain a clearly labelled fallback when no mapped use supports a classification.

The activity snapshot contains 8,194 OSM records, producing 8,379 usable polygon
components. Its OSM base timestamp is 2026-09-06 05:30:09 UTC. The committed gzip,
exact query and uncompressed SHA-256 in the output metadata preserve provenance.
All OSM inputs and derivatives are attributed under ODbL 1.0.

| Profile | Forms | Classification basis | Forms |
| --- | ---: | --- | ---: |
| Residential | 25,878 | Building tags | 26,307 |
| Office / daytime use | 6,787 | Parent-building tags | 692 |
| Retail | 986 | Spatial land-use inference | 6,568 |
| Hotel / overnight use | 614 | Documented research corrections | 10 |
| Mixed / unknown | 8,627 | Estimated fallback | 9,315 |

The inspector states both the selected use and its evidence category. Commercial
land use does not prove a particular tenant is an office; this remains an estimate.
No household occupancy, population statistics or live business activity is inferred.

Thirteen forms have separate lower-floor retail lighting: ten researched landmark
parts and three homes with shop/mixed-use tags. Hysan's 80 m division follows an
existing building-part break; IFC's 30 m podium and shop-house 3.5 m division are
illustrative. These are not surveyed retail boundaries. Some tall IFC parts
inherited a mall name in the earlier massing import; the correction applies an
office schedule above their illustrative podium without renaming the source.
Other untagged mixed-use towers are not assumed to have a retail podium.

## Schedule and atmosphere assumptions

The user's requested evening pattern drives the simulation: offices wind down
from 18:00, with some working through 20:00 and a small midnight reserve;
retail begins closing at 21:00, mostly closes by 23:00 and retains a few late shops;
homes fill up around 21:00, peak at 22:00 and begin sleeping around 23:00. The cited retail hours support later retail activity,
but neither they nor the planning sources establish the exact window probabilities.
The 04:00 minimum, sleep/wake curves and remaining lights are design choices.
The subsequent visual direction makes midnight as quiet as the earlier 04:00
setting, and reduces the 04:00 reserve further: 0.6% nominal home activation,
0.2% offices/retail, 0.4% mixed and 4.5% overnight services. These percentages
are art direction, not claims about real Hong Kong occupancy.
A single generic weekday/weekend curve currently serves each use category.

Distant light variation is a restrained visual approximation of atmospheric
transmission and turbulence. [ESO's explanation of scintillation](https://supernova.eso.org/exhibition/0818/?lang=en)
describes turbulence changing apparent light intensity; it concerns astronomical
sources and does not calibrate this city's terrestrial window effect.
The shader keeps nearby windows steady, gradually introduces at most ±4.5%
low-frequency modulation over 650–3,500 m, and applies gradual distance attenuation.
Windows use different phases; unresolved distant windows blend into a building
average to reduce aliasing. This is not a model of current humidity, aerosols or
weather. The effect can be switched off and follows reduced-motion preferences.
The integrated build now connects live/manual weather and dated astronomy;
remaining original-game parity is tracked separately.
