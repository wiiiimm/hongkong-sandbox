"""155 complete source-defined visual assemblies, no opening or structural claim.

The complete original perimeter is associated with independently qualified
same-actor hosts in the unchanged finite .1m band. Interiors may be free and
their old negatives stay explicit. The caller must independently pin actual
source assets, completed current-ground jobs and their expected bindings.
"""
import numpy as np
import hashlib,json
MODES=['providerOriginal','capturedLiteral','explicitLeftAssociatedF32ModelMatrix','explicitBalancedF32ModelMatrix']
SOURCE_SHA={'landsd/222465:0':'812a7583ff6a789ac956154a534a3548c8c6d5bfdff94338d13a79c42051a37c','landsd/223206:0':'fd67218f6828e36899e689d071c55bf95fa0df159ac2927643be46eead74d347'}
def canonical(x):return hashlib.sha256(json.dumps(x,sort_keys=True,separators=(',',':'),allow_nan=False).encode()).hexdigest()
def world_sha(w):return hashlib.sha256(np.asarray(w,np.float64).tobytes()).hexdigest()
def key(edge):return tuple(sorted(tuple(float(v)for v in p)for p in edge))
def edges(world,faces):
 from collections import defaultdict
 inventory=defaultdict(list)
 for f in faces:
  tri=world[f]
  for a,b in zip(tri,np.roll(tri,-1,axis=0)):
   if tuple(a)!=tuple(b):inventory[key([a,b])].append(f)
 return dict(inventory),{e for e,incident in inventory.items()if len(incident)==1}
from exact_original_shared_edge_component_census_v2_20261011 import census
from exact_original_body_boundary_group_census_v1_20261011 import census as boundary_census
from exact_original_edge_any_finite_distance_band_v2_20261010 import verify as finite_edge

NAMED_SOURCE_PART_FACES={0: [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13], 1: [14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27], 2: [28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41], 3: [42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55], 4: [56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69], 5: [70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80, 81, 82, 83], 6: [84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97], 21: [286, 287, 288, 289, 290, 291, 292, 293, 294, 295], 22: [296, 297, 298, 299, 300, 301, 302, 303, 304, 305], 23: [306, 307, 308, 309, 310, 311, 312, 313, 314, 315], 24: [316, 317, 318, 319, 320, 321, 322, 323, 324, 325], 25: [326, 327, 328, 329, 330, 331, 332, 333, 334, 335], 26: [336, 337, 338, 339, 340, 341, 342, 343, 344, 345], 27: [346, 347, 348, 349, 350, 351, 352, 353, 354, 355], 28: [356, 357, 358, 359, 360, 361, 362, 363, 364, 365], 29: [366, 367, 368, 369, 370, 371, 372, 373, 374, 375], 30: [376, 377, 378, 379, 380, 381, 382, 383, 384, 385], 31: [386, 387, 388, 389, 390, 391, 392, 393, 394, 395], 32: [396, 397, 398, 399, 400, 401, 402, 403, 404, 405], 33: [406, 407, 408, 409, 410, 411, 412, 413, 414, 415], 34: [416, 417, 418, 419, 420, 421, 422, 423, 424, 425], 35: [426, 427, 428, 429, 430, 431, 432, 433, 434, 435], 36: [436, 437, 438, 439, 440, 441, 442, 443, 444, 445], 37: [446, 447, 448, 449, 450, 451, 452, 453, 454, 455], 38: [456, 457, 458, 459, 460, 461, 462, 463, 464, 465], 39: [466, 467, 468, 469, 470, 471, 472, 473, 474, 475], 40: [476, 477, 478, 479, 480, 481, 482, 483, 484, 485], 41: [486, 487, 488, 489, 490, 491, 492, 493, 494, 495], 42: [496, 497, 498, 499, 500, 501, 502, 503, 504, 505], 66: [736, 737, 738, 739, 740, 741, 742, 743, 744, 745], 67: [746, 747, 748, 749, 750, 751, 752, 753, 754, 755], 68: [756, 757, 758, 759, 760, 761, 762, 763, 764, 765], 69: [766, 767, 768, 769, 770, 771, 772, 773, 774, 775], 70: [776, 777, 778, 779, 780, 781, 782, 783, 784, 785], 71: [786, 787, 788, 789, 790, 791, 792, 793, 794, 795], 72: [796, 797, 798, 799, 800, 801, 802, 803, 804, 805], 73: [806, 807, 808, 809, 810, 811, 812, 813, 814, 815], 74: [816, 817, 818, 819, 820, 821, 822, 823, 824, 825], 75: [826, 827, 828, 829, 830, 831, 832, 833, 834, 835], 76: [836, 837, 838, 839, 840, 841, 842, 843, 844, 845], 77: [846, 847, 848, 849, 850, 851, 852, 853, 854, 855], 78: [856, 857, 858, 859, 860, 861, 862, 863, 864, 865], 79: [866, 867, 868, 869, 870, 871, 872, 873, 874, 875], 80: [876, 877, 878, 879, 880, 881, 882, 883, 884, 885], 81: [886, 887, 888, 889, 890, 891, 892, 893, 894, 895], 82: [896, 897, 898, 899, 900, 901, 902, 903, 904, 905], 83: [906, 907, 908, 909, 910, 911, 912, 913, 914, 915], 84: [916, 917, 918, 919, 920, 921, 922, 923, 924, 925], 85: [926, 927, 928, 929, 930, 931, 932, 933, 934, 935], 88: [956, 957, 958, 959, 960, 961, 962, 963, 964, 965], 89: [966, 967, 968, 969, 970, 971, 972, 973, 974, 975], 91: [978, 979, 980, 981, 982, 983, 984, 985, 986, 987], 92: [988, 989, 990, 991, 992, 993, 994, 995, 996, 997], 93: [998, 999, 1000, 1001, 1002, 1003, 1004, 1005, 1006, 1007], 94: [1008, 1009, 1010, 1011, 1012, 1013, 1014, 1015, 1016, 1017], 95: [1018, 1019, 1020, 1021, 1022, 1023, 1024, 1025, 1026, 1027], 96: [1028, 1029, 1030, 1031, 1032, 1033, 1034, 1035, 1036, 1037], 97: [1038, 1039, 1040, 1041, 1042, 1043, 1044, 1045, 1046, 1047], 98: [1048, 1049, 1050, 1051, 1052, 1053, 1054, 1055, 1056, 1057], 99: [1058, 1059, 1060, 1061, 1062, 1063, 1064, 1065, 1066, 1067], 100: [1068, 1069, 1070, 1071, 1072, 1073, 1074, 1075, 1076, 1077], 101: [1078, 1079, 1080, 1081, 1082, 1083, 1084, 1085, 1086, 1087], 102: [1088, 1089, 1090, 1091, 1092, 1093, 1094, 1095, 1096, 1097], 103: [1098, 1099, 1100, 1101, 1102, 1103, 1104, 1105, 1106, 1107], 104: [1108, 1109, 1110, 1111, 1112, 1113, 1114, 1115, 1116, 1117], 106: [1120, 1121, 1122, 1123, 1124, 1125, 1126, 1127, 1128, 1129], 107: [1130, 1131, 1132, 1133, 1134, 1135, 1136, 1137, 1138, 1139], 108: [1140, 1141, 1142, 1143, 1144, 1145, 1146, 1147, 1148, 1149], 109: [1150, 1151, 1152, 1153, 1154, 1155, 1156, 1157, 1158, 1159], 111: [1162, 1163, 1164, 1165, 1166, 1167, 1168, 1169, 1170, 1171], 112: [1172, 1173, 1174, 1175, 1176, 1177, 1178, 1179, 1180, 1181], 157: [1622, 1623, 1624, 1625, 1626, 1627, 1628, 1629, 1630, 1631], 202: [2072, 2073, 2074, 2075, 2076, 2077, 2078, 2079, 2080, 2081], 224: [2302, 2303, 2304, 2305, 2306, 2307, 2308, 2309, 2310, 2311], 226: [2322, 2323, 2324, 2325, 2326, 2327, 2328, 2329, 2330, 2331], 227: [2332, 2333, 2334, 2335, 2336, 2337, 2338, 2339, 2340, 2341], 228: [2342, 2343, 2344, 2345, 2346, 2347, 2348, 2349, 2350, 2351], 229: [2352, 2353, 2354, 2355, 2356, 2357, 2358, 2359, 2360, 2361], 230: [2362, 2363, 2364, 2365, 2366, 2367, 2368, 2369, 2370, 2371], 231: [2372, 2373, 2374, 2375, 2376, 2377, 2378, 2379, 2380, 2381], 232: [2382, 2383, 2384, 2385, 2386, 2387, 2388, 2389, 2390, 2391], 233: [2392, 2393, 2394, 2395, 2396, 2397, 2398, 2399, 2400, 2401], 234: [2402, 2403, 2404, 2405, 2406, 2407, 2408, 2409, 2410, 2411], 235: [2412, 2413, 2414, 2415, 2416, 2417, 2418, 2419, 2420, 2421], 236: [2422, 2423, 2424, 2425, 2426, 2427, 2428, 2429, 2430, 2431], 237: [2432, 2433, 2434, 2435, 2436, 2437, 2438, 2439, 2440, 2441], 238: [2442, 2443, 2444, 2445, 2446, 2447, 2448, 2449, 2450, 2451], 239: [2452, 2453, 2454, 2455, 2456, 2457, 2458, 2459, 2460, 2461], 240: [2462, 2463, 2464, 2465, 2466, 2467, 2468, 2469, 2470, 2471], 241: [2472, 2473, 2474, 2475, 2476, 2477, 2478, 2479, 2480, 2481], 242: [2482, 2483, 2484, 2485, 2486, 2487, 2488, 2489, 2490, 2491], 243: [2492, 2493, 2494, 2495, 2496, 2497, 2498, 2499, 2500, 2501], 245: [2512, 2513, 2514, 2515, 2516, 2517, 2518, 2519, 2520, 2521], 246: [2522, 2523, 2524, 2525, 2526, 2527, 2528, 2529, 2530, 2531], 247: [2532, 2533, 2534, 2535, 2536, 2537, 2538, 2539, 2540, 2541], 248: [2542, 2543, 2544, 2545, 2546, 2547, 2548, 2549, 2550, 2551], 249: [2552, 2553, 2554, 2555, 2556, 2557, 2558, 2559, 2560, 2561], 250: [2562, 2563, 2564, 2565, 2566, 2567, 2568, 2569, 2570, 2571], 251: [2572, 2573, 2574, 2575, 2576, 2577, 2578, 2579, 2580, 2581], 252: [2582, 2583, 2584, 2585, 2586, 2587, 2588, 2589, 2590, 2591], 253: [2592, 2593, 2594, 2595, 2596, 2597, 2598, 2599, 2600, 2601], 254: [2602, 2603, 2604, 2605, 2606, 2607, 2608, 2609, 2610, 2611], 255: [2612, 2613, 2614, 2615, 2616, 2617, 2618, 2619, 2620, 2621], 256: [2622, 2623, 2624, 2625, 2626, 2627, 2628, 2629, 2630, 2631], 257: [2632, 2633, 2634, 2635, 2636, 2637, 2638, 2639, 2640, 2641], 258: [2642, 2643, 2644, 2645, 2646, 2647, 2648, 2649, 2650, 2651], 259: [2652, 2653, 2654, 2655, 2656, 2657, 2658, 2659, 2660, 2661], 260: [2662, 2663, 2664, 2665, 2666, 2667, 2668, 2669, 2670, 2671], 261: [2672, 2673, 2674, 2675, 2676, 2677, 2678, 2679, 2680, 2681], 262: [2682, 2683, 2684, 2685, 2686, 2687, 2688, 2689, 2690, 2691], 263: [2692, 2693, 2694, 2695, 2696, 2697, 2698, 2699, 2700, 2701], 264: [2702, 2703, 2704, 2705, 2706, 2707, 2708, 2709, 2710, 2711], 266: [2722, 2723, 2724, 2725, 2726, 2727, 2728, 2729, 2730, 2731], 267: [2732, 2733, 2734, 2735, 2736, 2737, 2738, 2739, 2740, 2741], 268: [2742, 2743, 2744, 2745, 2746, 2747, 2748, 2749, 2750, 2751], 269: [2752, 2753, 2754, 2755, 2756, 2757, 2758, 2759, 2760, 2761], 270: [2762, 2763, 2764, 2765, 2766, 2767, 2768, 2769, 2770, 2771], 271: [2772, 2773, 2774, 2775, 2776, 2777, 2778, 2779, 2780, 2781], 272: [2782, 2783, 2784, 2785, 2786, 2787, 2788, 2789, 2790, 2791], 273: [2792, 2793, 2794, 2795, 2796, 2797, 2798, 2799, 2800, 2801], 274: [2802, 2803, 2804, 2805, 2806, 2807, 2808, 2809, 2810, 2811], 275: [2812, 2813, 2814, 2815, 2816, 2817, 2818, 2819, 2820, 2821], 276: [2822, 2823, 2824, 2825, 2826, 2827, 2828, 2829, 2830, 2831], 277: [2832, 2833, 2834, 2835, 2836, 2837, 2838, 2839, 2840, 2841], 278: [2842, 2843, 2844, 2845, 2846, 2847, 2848, 2849, 2850, 2851], 279: [2852, 2853, 2854, 2855, 2856, 2857, 2858, 2859, 2860, 2861], 280: [2862, 2863, 2864, 2865, 2866, 2867, 2868, 2869, 2870, 2871], 281: [2872, 2873, 2874, 2875, 2876, 2877, 2878, 2879, 2880, 2881], 282: [2882, 2883, 2884, 2885, 2886, 2887, 2888, 2889, 2890, 2891], 283: [2892, 2893, 2894, 2895, 2896, 2897, 2898, 2899, 2900, 2901], 284: [2902, 2903, 2904, 2905, 2906, 2907, 2908, 2909, 2910, 2911], 285: [2912, 2913, 2914, 2915, 2916, 2917, 2918, 2919, 2920, 2921], 286: [2922, 2923, 2924, 2925, 2926, 2927, 2928, 2929, 2930, 2931], 289: [2948, 2949, 2950, 2951, 2952, 2953, 2954, 2955, 2956, 2957], 290: [2958, 2959, 2960, 2961, 2962, 2963, 2964, 2965, 2966, 2967], 403: [4056, 4057, 4058, 4059, 4060, 4061, 4062, 4063, 4064, 4065], 423: [4256, 4257, 4258, 4259, 4260, 4261, 4262, 4263, 4264, 4265], 512: [5572, 5573, 5574, 5575, 5576, 5577, 5578, 5579, 5580, 5581], 513: [5582, 5583, 5584, 5585, 5586, 5587, 5588, 5589, 5590, 5591], 514: [5592, 5593, 5594, 5595, 5596, 5597, 5598, 5599, 5600, 5601], 515: [5602, 5603, 5604, 5605, 5606, 5607, 5608, 5609, 5610, 5611], 516: [5612, 5613, 5614, 5615, 5616, 5617, 5618, 5619, 5620, 5621], 517: [5622, 5623, 5624, 5625, 5626, 5627, 5628, 5629, 5630, 5631], 518: [5632, 5633, 5634, 5635, 5636, 5637, 5638, 5639, 5640, 5641], 519: [5642, 5643, 5644, 5645, 5646, 5647, 5648, 5649, 5650, 5651], 520: [5652, 5653, 5654, 5655, 5656, 5657, 5658, 5659, 5660, 5661], 521: [5662, 5663, 5664, 5665, 5666, 5667, 5668, 5669, 5670, 5671], 522: [5672, 5673, 5674, 5675, 5676, 5677, 5678, 5679, 5680, 5681], 523: [5682, 5683, 5684, 5685, 5686, 5687, 5688, 5689, 5690, 5691], 524: [5692, 5693, 5694, 5695, 5696, 5697, 5698, 5699, 5700, 5701], 525: [5702, 5703, 5704, 5705, 5706, 5707, 5708, 5709, 5710, 5711], 526: [5712, 5713, 5714, 5715, 5716, 5717, 5718, 5719, 5720, 5721], 527: [5722, 5723, 5724, 5725, 5726, 5727, 5728, 5729, 5730, 5731], 563: [6082, 6083, 6084, 6085, 6086, 6087, 6088, 6089, 6090, 6091], 1106: [13470, 13471, 13472, 13473]}

def binding(part,uid,source_sha,worlds,contexts,qualified_hosts):
 return dict(part=part,uid=uid,sourceSHA256=source_sha,
  originalFaceIds=NAMED_SOURCE_PART_FACES.get(part),
  completeOwnedWorldSHA256={m:world_sha(worlds[m])for m in MODES},
  completedPartContextSHA256={m:canonical(contexts[m])for m in MODES},
  qualifiedNonvisualHostFacesSHA256={m:canonical(sorted(qualified_hosts[m]))for m in MODES})

def verify(part,uid,source_sha,worlds,contexts,qualified_hosts,*,expected_binding):
 assert part in NAMED_SOURCE_PART_FACES,'Not a named original visual assembly'
 faces=NAMED_SOURCE_PART_FACES[part]
 actor='landsd/222465:0'if max(faces)<13063 else'landsd/223206:0'
 assert uid==actor and source_sha==SOURCE_SHA[actor]
 assert set(worlds)==set(contexts)==set(qualified_hosts)==set(MODES)
 arrays={m:np.asarray(worlds[m],np.float64)for m in MODES}
 assert all(w.shape==(13519,3,3)and np.isfinite(w).all()for w in arrays.values())
 bound=binding(part,uid,source_sha,arrays,contexts,qualified_hosts)
 assert bound==expected_binding,'Frozen source/current/host binding changed'
 original=arrays['providerOriginal'];_,source_boundary=edges(original,faces)
 assert source_boundary,'Original visual assembly has no complete boundary'
 results=[]
 for mode in MODES:
  w=arrays[mode];ctx=contexts[mode];a=ctx['association'];f=ctx['allCompletePartFiniteFaces']
  assert ctx['completeOwnedWorldSHA256']==world_sha(w)
  assert a['originalBody']==part and a['actorUID']==actor and a['completeOriginalFaceIds']==faces
  c=census(w,faces)
  assert c['sharedEdgeConnectedComponents']==[faces]and not c['exactNonrenderingOriginalFaces']
  b=boundary_census(w,faces);groups=b['completeIncidenceOneBoundaryGroups']
  assert len(groups)==1 and groups[0]['closedConnectedDegreeTwoLoop']is True,'Incomplete original perimeter'
  _,boundary=edges(w,faces);correspondence={}
  for orig,actual in zip(original[faces].reshape(-1,3),w[faces].reshape(-1,3)):
   o=tuple(orig);v=tuple(actual)
   if o in correspondence:assert correspondence[o]==v,'Original shared vertex split'
   correspondence[o]=v
  assert len(set(correspondence.values()))==len(correspondence),'Original nonzero vertices collapsed'
  assert {key([correspondence[x]for x in e])for e in source_boundary}==boundary
  hs=a['completeHostSelection'];selected=set(hs['selectedGlobalHostFaces']);qualified=set(qualified_hosts[mode])
  assert selected and selected<=qualified and not selected&set(faces)
  assert all((h<13063)==(actor=='landsd/222465:0')for h in selected)
  assert hs['exactFixedBandM']==.1 and hs['allSelectedHostsBelongToNonvisualQualifiedPaths']is True
  assert hs['actualSelectedHostWorldSHA256']==world_sha(w[sorted(selected)])
  assert hs['completeQualifiedSameActorHostFaces']==sorted(qualified)
  assert not census(w,sorted(selected))['exactNonrenderingOriginalFaces'],'Degenerate host credit'
  offset=0 if actor=='landsd/222465:0'else 13063
  assert [z['sourceFace']+offset for z in f]==faces
  assert all(z['completeActualFacetSHA256']==world_sha(w[z['sourceFace']+offset])for z in f),'Stale finite source facet binding'
  assert all(z['closedProjectionCovered']is True and z['existingOrdinaryClearanceBoundProved']is True
   and z['strictlyExposedWholeFacet']is True for z in f)
  raw=a['allActualIncidenceOneBoundaryEdgeProofs']
  ep={key(e['completeActualBoundaryEdge']):e for e in raw}
  assert len(ep)==len(raw)and set(ep)==boundary,'Partial or duplicate perimeter proof'
  checked=[]
  for edge in sorted(boundary):
   prior=ep[edge]
   assert prior['wholeEdgeWithinExistingFiniteHostBand']is True
   assert prior['actualSubsetWholeEdgeHostProofVerbatim']['verifiedCompleteOriginalEdgeFiniteFacadeBand']is True
   proof=finite_edge(np.asarray(edge,float),w[sorted(selected)])
   assert proof['strictBandM']==.1 and proof['verifiedCompleteOriginalEdgeFiniteFacadeBand']is True,'Actual complete edge detached'
   checked.append(dict(completeActualEdge=edge,independentWholeFiniteEdgeProof=proof))
  results.append(dict(mode=mode,completeSourcePerimeterEdgeCount=len(boundary),
   independentCompletePerimeterProofs=checked,completePartFiniteClearance=True,
   originalInteriorFindingsVerbatim=a['allActualFacetProofs'],
   wholeInteriorBandPositive=a['allFacetsWithinFixedBand'],
   completeOriginalTopologyVerbatim=c,completeOriginalBoundaryInventory=b))
 return dict(contract='twin155-named-complete-open-boundary-associated-original-visual-assembly-proposal-v1',
  binding=bound,originalBody=part,uid=uid,completeOriginalFaces=faces,
  namedSourceVisualInterpretation='original-complete-back-boundary-associated-facade-or-roof-visual-assembly',
  allFourStreamProofs=results,conditionalSourceVisualRoleProposal=True,
  originalInteriorNegativesPreserved=True,wholeInteriorProximityNotCertified=True,
  originalOpeningOrHoleCertified=False,sourceFunctionInferred=False,
  structuralRootCredit=False,structuralBridgeCredit=False,visualPartsNeverQualifyHosts=True,
  nativeReacceptance=False,currentAcceptance=False,sourceGeometryChanges=0,newlyInstalled=0)
