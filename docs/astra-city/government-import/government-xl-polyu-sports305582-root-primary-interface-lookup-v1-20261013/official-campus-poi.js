//var campusCenterLocation = {lat: 22.30434563, lng: 114.179925};
var campusCenterLocation     = {lat:22.304960921294402, lng:114.17942379083775};
var campusUpperLeftBoundary  = {lat:22.300257, lng:114.177186};
var campusLowerRightBoundary = {lat:22.307547, lng:114.184798};

var campusPoiTypeLabel = {
	AcademicOffice: 'LBL0008',
	AdministrativeOffice: 'LBL0029',
	Block: 'LBL0009',
	Canteen: 'LBL0006',
	CoreLocation: 'LBL0025',
	Building: 'LBL0023',
	Toilet: 'LBL0007',
	AccessibleToilet: 'LBL0007',
	Clinic: 'LBL0019',
	LectureTheatre: 'LBL0020',
	PublicTransport: 'LBL0040',
	Bank: 'LBL0041',
	Aed: 'LBL0019',
	ResearchCentre: 'LBL0024',
	LactationRoom: 'LBL0025', 
	PrayerRoom: 'LBL0026'

};

var gCampusPois = {
	// member variables
	inited: false,
	officeWebVOs: [],
	academicofficeWebVOs: [],
	administrativeofficeWebVOs: [],
	blockWebVOs: [],
	canteenWebVOs: [],
	buildingWebVOs: [],
	toiletWebVOs: [],
	accessibletoiletWebVOs: [],
	clinicWebVOs: [],
	lecturetheatreWebVOs: [],
	coreLocationWebVOs: [],
	publictransportWebVOs: [],
	bankWebVOs: [],
	bookstoreWebVOs: [],
	carparkWebVOs: [],
	postboxWebVOs: [],
	waterstationWebVOs: [],
	sportsFacilitiesWebVOs: [],
	aedWebVOs: [],
	researchcentreWebVOs: [],
	lactationroomWebVOs: [],
	prayerroomWebVOs: [],
	// member functions
	init: function(next) {
		gCampusPois._loadData('Bank,Building,Bookstore,CoreLocation,Canteen,Toilet,LectureTheatre,Clinic,AcademicOffice,AdministrativeOffice,PublicTransport,Postbox,WaterStation,AED,ResearchCentre,LactationRoom,PrayerRoom');
	},
	listPoiCategory: function() {
		return ['AcademicOffice','AdministrativeOffice','Building','Bookstore','CarPark','CoreLocation','Canteen','LectureTheatre','Clinic','Toilet','AccessibleToilet','Bank','PublicTransport','Postbox','WaterStation','SportsFacility','AED','ResearchCentre','LactationRoom','PrayerRoom'];
	},
	listPoiDataTableVOsByPoiType: function(poiType) {
		var poiDataTableVOs = [];
		var poiWebVOs = gCampusPois.listPoiWebVOsByPoiType(poiType);
		for (i=0 ; i<poiWebVOs.length ; i++) {
			var dataTableVO = [getLabelByLang(poiWebVOs[i].getPoiTypeLabel(), currentLanguage), poiWebVOs[i].getPoiName(currentLanguage) +  '<br/>' + '<img src="./img/pin-poi-loc.png" style="height:20px; margin-top:5px"/>' + '<text style="color:#777777; height:20px;">' + poiWebVOs[i].getPoiAddr(currentLanguage) + '</text>', poiWebVOs[i].getPoiObjectId()];
			poiDataTableVOs.push(dataTableVO);
		}
		return poiDataTableVOs;
	},
	listPoiWebVOsByPoiType: function(poiType) {
		if (poiType == 'Office') {
			return this.officeWebVOs;
		} else if (poiType == 'AcademicOffice') {
			return this.academicofficeWebVOs;
		} else if (poiType == 'AdministrativeOffice') {
			return this.administrativeofficeWebVOs;
		} else if (poiType == 'Block') {
			return this.blockWebVOs;
		} else if (poiType == 'Bookstore') {
			return this.bookstoreWebVOs;
		} else if (poiType == 'CarPark') {
			return this.carparkWebVOs;
		} else if (poiType == 'Canteen') {
			return this.canteenWebVOs;
		} else if (poiType == 'CoreLocation') {
			return this.coreLocationWebVOs;
		} else if (poiType == 'Building') {
			return this.buildingWebVOs;
		} else if (poiType == 'Toilet') {
			return this.toiletWebVOs;
		} else if (poiType == 'AccessibleToilet') {
			return this.accessibletoiletWebVOs;
		} else if (poiType == 'Clinic') {
			return this.clinicWebVOs;
		} else if (poiType == 'LectureTheatre') {
			return this.lecturetheatreWebVOs;
		} else if (poiType == 'PublicTransport') {
			return this.publictransportWebVOs;
		} else if (poiType == 'Postbox') {
			return this.postboxWebVOs;
		} else if (poiType == 'WaterStation') {
			return this.waterstationWebVOs;
		} else if (poiType == 'SportsFacility') {
			return this.sportsFacilitiesWebVOs;
		} else if (poiType == 'Bank') {
			return this.bankWebVOs;
		} else if (poiType == 'AED') {
			return this.aedWebVOs;
		} else if (poiType == 'ResearchCentre') {
			return this.researchcentreWebVOs;
		} else if (poiType == 'LactationRoom') {
			return this.lactationroomWebVOs;
		} else if (poiType == 'PrayerRoom') {
			return this.prayerroomWebVOs;
		}
	},
	listPoiWebVOsByKeyword: function(keyword) {
		var resultPoiWebVOs = [];
		var searchPattern = new RegExp(keyword,"i"); 
		var poiCategories = this.listPoiCategory();
		for (var i=0 ; i<poiCategories.length ; i++) {
			poiWebVOs = this.listPoiWebVOsByPoiType(poiCategories[i]);
			for (var j=0 ; j<poiWebVOs.length ; j++) {
				//if (poiWebVOs[j].getPoiNameByLang('en_US').match(searchPattern) || poiWebVOs[j].getPoiName().match(searchPattern)) {
				if (poiWebVOs[j].getPoiNameByLang('en_US').match(searchPattern) || poiWebVOs[j].getPoiNameByLang('zh_HK').match(searchPattern) || poiWebVOs[j].getPoiNameByLang('zh_CN').match(searchPattern)) {
					resultPoiWebVOs.push(poiWebVOs[j]);
				}
			}
		}
		return resultPoiWebVOs;
	},	
	getPoiWebVOByPoiObjectId: function(poiType, poiObjectId) { 
		var i;
		var poiWebVOs = this.listPoiWebVOsByPoiType(poiType);
		for (i = 0; poiWebVOs != null && i < poiWebVOs.length; i++) { 
			if (poiWebVOs[i].getPoiObjectId() == poiObjectId) {				
				return poiWebVOs[i];
			}
		}
		return null;
	},
	getPoiWebVOByPoiName: function(poiType, poiName) { 
		var i;
		var poiWebVOs = this.listPoiWebVOsByPoiType(poiType);
		if (poiName === 'Carpark') poiWebVOs = this.carparkWebVOs;
		if (poiName === 'Bank') poiWebVOs = this.bankWebVOs;
		if (poiName === 'Bookstore') poiWebVOs = this.bookstoreWebVOs;
		if (poiName === 'Postbox') poiWebVOs = this.postboxWebVOs;
		for (i = 0; poiWebVOs != null && i < poiWebVOs.length; i++) { 
			if (poiWebVOs[i].getPoiNameByLang(languages.en_US) == poiName.replace(/[\']/g, "\\x27").replace(/[\"]/g, " ")) {
				return poiWebVOs[i];
			}
		}
		return null;
	},
	getPoiWebVOByPoiLocCode: function(poiType, poiLocCode) {
		var i;
		var poiWebVOs = this.listPoiWebVOsByPoiType(poiType);
		for (i = 0; poiWebVOs != null && i < poiWebVOs.length; i++) { 
			if (poiWebVOs[i].getPoiLocCode() != null && 
					(poiWebVOs[i].getPoiLocCode().indexOf((poiLocCode+',')) == 0 || poiWebVOs[i].getPoiLocCode().indexOf((','+poiLocCode+',')) > 0)) {
				return poiWebVOs[i];
			}
		}
		return null;
	},
	getPoiWebVOsByPoiLocation: function(poiType, poiLocation) { 
		var i, poiWebVOs = [];
		var poiWebVOsByType = this.listPoiWebVOsByPoiType(poiType);
		for (i = 0; poiWebVOsByType != null && i < poiWebVOsByType.length; i++) { 
			if (poiWebVOsByType[i].getPoiLocation() == poiLocation) {				
				poiWebVOs.push(poiWebVOsByType[i]);				
			}
		}
		return poiWebVOs;
	},
	tranformModelVoToWebVo: function(poiType, poiModelVO) {
		poiModelVO.poiType = poiType;
		return {
			_vo: poiModelVO,
			getDestMarkerLatLng: function() {
				return {lat: Number(this['_vo']['marker']['latitude']), lng: Number(this['_vo']['marker']['longitude'])};
			},
			getMapMarkerLatLng: function() {
				return {lat: Number(this['_vo']['mapmarker']['latitude']), lng: Number(this['_vo']['mapmarker']['longitude'])};
			},
			getWayPtLatLng: function() {
				return {lat: Number(this['_vo']['waypoint']['latitude']), lng: Number(this['_vo']['waypoint']['longitude'])};
			},
			getPoiObjectId: function() {
				return this['_vo']['id'];
			},
			getPoiName: function() {
				return this['_vo']['name'][currentLanguage].replace(/[\"]/g, " ");
			},
			getPoiNameByLang: function(lang) {
				return this['_vo']['name'][lang].replace(/[\']/g, "\\x27").replace(/[\"]/g, " ");
			},
			getPoiImageFile: function() {
				return (this['_vo']['img'] != null && this['_vo']['img']['filename'] != null) ? this['_vo']['img']['filename'] : null;
			},
			getPoiImageUrl: function() {
				switch (this.getPoiType()) {
					case 'LactationRoom':
					case 'PrayerRoom':
					case 'AED':
						return (this['_vo']['img'] != null && this['_vo']['img']['url'] != null) ? encodeURI(this['_vo']['img']['url'].replace("/kiosk/","/campus-map/")) : null;
					default:
						return this.getPoiLocImageUrl();
				}
			},
			getPoiLocImageUrl: function() {
				switch (this.getPoiType()) {
					case 'LactationRoom':
					case 'PrayerRoom':
					case 'AED':
						// show location photo for selected poi category
						var buildingWebVO = gCampusPois.buildingWebVOs.find(vo => vo.getPoiLocation() == this.getPoiLocation()) ? 
							gCampusPois.buildingWebVOs.find(vo => vo.getPoiLocation() == this.getPoiLocation())['_vo']['img'] : undefined;
						return buildingWebVO ? buildingWebVO['url'].replace("/kiosk/","/campus-map/") : null;
					default:
						return (this['_vo']['img'] != null && this['_vo']['img']['url'] != null) ? encodeURI(this['_vo']['img']['url'].replace("/kiosk/","/campus-map/")) : null;					
				}
			},
			getPoiLocation: function() {
				return this['_vo']['loc'];
			},			
			getPoiLocCode: function() {
				return this['_vo']['locCode'];
			},
			getPoiOpeningHour: function() {
				gLogger.log("DEBUG", this['_vo']['openingHours']);
				gLogger.log("DEBUG", this['_vo']['openingHours']['PublicHolidayFlag']);
				gLogger.log("DEBUG", this['_vo']['openingHours']['PublicHoliday']);
				if (this['_vo']['openingHours'] == undefined) {
					return '';
				} else if (this['_vo']['openingHours']['PublicHolidayFlag'] == 'Y' && this['_vo']['openingHours']['PublicHoliday'] != undefined) {
					return this['_vo']['openingHours']['PublicHoliday'];
				} else {
					return this['_vo']['openingHours'][['Sun','Mon','Tue','Wed','Thu','Fri','Sat'][new Date().getDay()]];
				}
			},
			getPoiInfo: function(lang) {
				return this['_vo']['info'][lang];
			},
			getPoiAddr: function() {
				return this['_vo']['addr'][currentLanguage].replace(/[\"]/g, " ");
			},
			getPoiAddrByLang: function(lang) {
				return this['_vo']['addr'][lang].replace(/[\"]/g, " ");
			},
			getPoiNearbyBuildings: function() {
				return this['_vo']['buildingNearby'];
			},
			getPoiNearbyCoreLocations: function() {
				return this['_vo']['coreLocationNearby'];
			},
			getPoiType: function() {
				return this['_vo']['poiType'];
			},
			getPoiTypeLabel: function() {
				return campusPoiTypeLabel[this['_vo']['poiType']];
			},
			getPoiDestWayPoints: function() {
				return [];
			},
			getPoiSportsFacilities: function() {
				if (this['_vo']['poiType'] == 'SportsFacility') {
					return this['_vo']['sportsFacilities'][currentLanguage];
				} else {
					return null;
				}
			},
			isHotWaterStation: function() {
				if (poiType == 'WaterStation') {
					return this['_vo']['hotWaterSupplied'];
				} else {
					return null;
				}
			},			
			getPoiSliderHtmlCode: function() {
				//return '<div class="slick-item" onclick="gCampusMap.DoWayfinding(gCampusPois.getPoiWebVOByPoiName(\''+ this['_vo']['poiType'] + '\',\'' + this['_vo']['name'][languages.en_US] + '\'),null);">' +
				return '<div class="slick-item">' +
						'<img class="slick-item-img" src="'+'./img/'+ this['_vo']['poiType'].toLowerCase() + '/' + this['_vo']['img']['filename'] +'" poiType="'+ this['_vo']['poiType'] + '" poiName="' + this['_vo']['name'][languages.en_US] + '"/>' +
						'<div id="slick-item-lbl" class="i18n-inline-label" ' + 
							'label_en_US="'+ this['_vo']['name'][languages.en_US] + '" ' + 
							'label_zh_HK="'+ this['_vo']['name'][languages.zh_HK] + '" ' + 
							'label_zh_CN="' + this['_vo']['name'][languages.zh_CN] + '">' + this['_vo']['name'][currentLanguage] +'</div>' +
					'</div>';
			},
			getSearchResultSliderHtmlCode: function() {
				var englishNameFontSize = textWidth(this['_vo']['name'][languages.en_US], "Arial, Microsoft JhengHei") > 180 ? 'font-size:11px;' : 'font-size:14px;';
				//return '<div class="slick-item" onclick="if (gSliderDragging == true) {return;} else {gPanelOfCampusPoiSearch.close(function(){gCampusMap.DoWayfinding(gCampusPois.getPoiWebVOByPoiName(\''+ this['_vo']['poiType'] + '\',\'' + this['_vo']['name'][languages.en_US] + '\'),null);});}">' +
				return '<div class="slick-item">' +
					'<img class="slick-item-img" src="'+'./img/'+ this['_vo']['poiType'].toLowerCase() + '/' + this['_vo']['img']['filename'] +'" poiType="'+ this['_vo']['poiType'] + '" poiName="' + this['_vo']['name'][languages.en_US] + '"/>' +
						'<div id="slick-item-header">' + getLabelByCurrLang(campusPoiTypeLabel[this['_vo']['poiType']]) + '</div>' +
						'<div id="slick-item-lbl" class="slick-item-lbl" poiType="'+ this['_vo']['poiType'] + '" poiName="' + this['_vo']['name'][languages.en_US] + '">' + ((currentLanguage != languages.en_US) ?  (this['_vo']['name'][currentLanguage] + '<br/><span style="' + englishNameFontSize + '">' + this['_vo']['name'][languages.en_US] + '</span>') : this['_vo']['name'][languages.en_US]) + '</div>' +
					'</div>';
			},
			getReferenceUrl: function() {
				return this['_vo']['referenceURL'];
			}
		};
	},
	_setWebVOs: function(poiType, modelVOs, next) {
		// Set POI data
		var i;
		for (i = 0; modelVOs != null && i < modelVOs.length; i++) {
			poiWebVO = gCampusPois.tranformModelVoToWebVo(modelVOs[i].category, modelVOs[i]);
			poiType=poiWebVO.getPoiType();
			if (poiType == 'AcademicOffice') {
				gCampusPois.academicofficeWebVOs.push(poiWebVO);	
				gCampusPois.officeWebVOs.push(poiWebVO);
			} else if (poiType == 'AdministrativeOffice') {
				gCampusPois.administrativeofficeWebVOs.push(poiWebVO);	
				gCampusPois.officeWebVOs.push(poiWebVO);
			} else if (poiType == 'Bank') {
				gCampusPois.bankWebVOs.push(poiWebVO);
			} else if (poiType == 'Building') {
				gCampusPois.buildingWebVOs.push(poiWebVO);
			} else if (poiType == 'Bookstore') {
				gCampusPois.bookstoreWebVOs.push(poiWebVO);
			} else if (poiType == 'Canteen') {
				gCampusPois.canteenWebVOs.push(poiWebVO);
			} else if (poiType == 'CoreLocation') {
				gCampusPois.coreLocationWebVOs.push(poiWebVO);
				if (poiWebVO['_vo']['sportsFacilities'] != undefined && poiWebVO['_vo']['sportsFacilities']['en_US'] != "") {
					var sportsFacilitiesWebVO = Object.assign({}, poiWebVO);
					sportsFacilitiesWebVO['_vo'] = JSON.parse(JSON.stringify(poiWebVO['_vo']));
					sportsFacilitiesWebVO['_vo']['poiType'] = 'SportsFacility';
					gCampusPois.sportsFacilitiesWebVOs.push(sportsFacilitiesWebVO);
				}
			} else if (poiType == 'Toilet' || poiType == 'AccessibleToilet') {
				if (poiWebVO['_vo']['toiletForDisabled'] == true) {
					poiWebVO['_vo']['poiType'] = 'AccessibleToilet';
					gCampusPois.accessibletoiletWebVOs.push(poiWebVO);
				} else {
					gCampusPois.toiletWebVOs.push(poiWebVO);
				}
			} else if (poiType == 'Clinic') {
				gCampusPois.clinicWebVOs.push(poiWebVO);
			} else if (poiType == 'LectureTheatre') {
				gCampusPois.lecturetheatreWebVOs.push(poiWebVO);
			} else if (poiType == 'Postbox') {
				gCampusPois.postboxWebVOs.push(poiWebVO);
			} else if (poiType == 'PublicTransport') {
				if (poiWebVO.getPoiNameByLang(languages.en_US).startsWith('Taxi ') || 
						poiWebVO.getPoiNameByLang(languages.en_US).startsWith('Bus Station ')) {
					gCampusPois.publictransportWebVOs.push(poiWebVO);
				} else if (poiWebVO.getPoiNameByLang(languages.en_US) == 'Carpark') {
					gCampusPois.carparkWebVOs.push(poiWebVO);
				}
				// if (poiWebVO.getPoiNameByLang(languages.en_US) == 'Taxi Station' || 
				// 		poiWebVO.getPoiNameByLang(languages.en_US) == 'Taxi Drop-off Point (To Block Z)' || 
				// 		poiWebVO.getPoiNameByLang(languages.en_US) == 'Taxi Drop-off Point (To Main Campus)' || 
				// 		poiWebVO.getPoiNameByLang(languages.en_US) == 'Bus Station (Hong Kong PolyU)' || 
				// 		poiWebVO.getPoiNameByLang(languages.en_US) == 'Bus Station (Hong Kong PolyU Phase 8)' || 
				// 		poiWebVO.getPoiNameByLang(languages.en_US) == 'Bus Station (Cross Harbour Tunnel Toll Plaza - Hong Kong Direction)' || 
				// 		poiWebVO.getPoiNameByLang(languages.en_US) == 'Bus Station (Cross Harbour Tunnel Toll Plaza - Kowloon Direction)') {
				// 	gCampusPois.publictransportWebVOs.push(poiWebVO);
				// } else if (poiWebVO.getPoiNameByLang(languages.en_US) == 'Carpark') {
				// 	gCampusPois.carparkWebVOs.push(poiWebVO);
				// }
			} else if (poiType == 'WaterStation') {
				gCampusPois.waterstationWebVOs.push(poiWebVO);
			} else if (poiType == 'AED') {
				gCampusPois.aedWebVOs.push(poiWebVO);
			} else if (poiType == 'ResearchCentre') {
				gCampusPois.researchcentreWebVOs.push(poiWebVO);
			} else if (poiType == 'LactationRoom') {
				gCampusPois.lactationroomWebVOs.push(poiWebVO);
			} else if (poiType == 'PrayerRoom') {
				gCampusPois.prayerroomWebVOs.push(poiWebVO);
			}
		}
		if (next != null) {
			next();
		}
	},
	_loadData: function(poiType, next) {
		gLogger.log("INFO", "Load "+poiType+" Starts");		
		var xmlhttp = new XMLHttpRequest();	
		xmlhttp.onreadystatechange = function() {
			if (this.readyState == 4 && this.status == 200) {
				gCampusPois._setWebVOs(poiType, JSON.parse(this.responseText).value, function(){
					gLogger.log("INFO", "Load "+poiType+" Success");
					gLogger.log("DEBUG", "academicofficeWebVOLoaded", gCampusPois.academicofficeWebVOs);
					gLogger.log("DEBUG", "administrativeofficeWebVOLoaded", gCampusPois.administrativeofficeWebVOs);
					gLogger.log("DEBUG", "bankWebVOLoaded", gCampusPois.bankWebVOs);
					gLogger.log("DEBUG", "bookstoreWebVOLoaded", gCampusPois.bookstoreWebVOs);
					gLogger.log("DEBUG", "buildingWebVOLoaded", gCampusPois.buildingWebVOs);
					gLogger.log("DEBUG", "carparkWebVOLoaded", gCampusPois.carparkWebVOs);
					gLogger.log("DEBUG", "canteenWebVOLoaded", gCampusPois.canteenWebVOs);
					gLogger.log("DEBUG", "coreLocationWebVOLoaded", gCampusPois.coreLocationWebVOs);
					gLogger.log("DEBUG", "clinicWebVOLoaded", gCampusPois.clinicWebVOs);
					gLogger.log("DEBUG", "lecturetheatreWebVOLoaded", gCampusPois.lecturetheatreWebVOs);
					gLogger.log("DEBUG", "toiletWebVOLoaded", gCampusPois.toiletWebVOs);
					gLogger.log("DEBUG", "publictransportWebVOLoaded", gCampusPois.publictransportWebVOs);
					gLogger.log("DEBUG", "postboxWebVOLoaded", gCampusPois.postboxWebVOs);
					gLogger.log("DEBUG", "waterstationWebVOLoaded", gCampusPois.waterstationWebVOs);
					gLogger.log("DEBUG", "sportsFacilityWebVOLoaded", gCampusPois.sportsFacilitiesWebVOs);
					gLogger.log("DEBUG", "aedWebVOLoaded", gCampusPois.aedWebVOs);
					gLogger.log("DEBUG", "researchcentreWebVOLoaded", gCampusPois.researchcentreWebVOs);
					gLogger.log("DEBUG", "lactionRoomWebVOLoaded", gCampusPois.lactationroomWebVOs);
					gLogger.log("DEBUG", "prayerRoomWebVOLoaded", gCampusPois.prayerroomWebVOs);
					gCampusPois.inited = true;
					if (next != null) {
						next();
					}
				});
			}
		};
		//xmlhttp.open("GET", "../public-data/"+poiType+"s?channel=campus-map", true);
		xmlhttp.open("GET", "../public-data/POIs?channel=campus-map&category="+poiType, true);
		xmlhttp.send();
	}
}


var campusLocations = {
	MTR_A1: {id:"MTR_A1", locType:"Entrance",
		wayPtPos:  {lat: 22.303719, lng: 114.180437}, 
		markerPos: null,
		markerObject: null,
		name: function(lang) {return getLabelByLang("LOC0001", lang);},
		getWayPtPos: function() {return this.wayPtPos;},
		getMarkerPos: function() {return this.markerPos;},
	},
};

