var   defaultZoomLevel = 18;
const minimumZoomLevel = 16;
const maximumZoomLevel = 19;

/**
 * Load Google Map JS
 */
function CreateCampusMap() {		
	var mapKey = 'AIzaSyBrymZYfvh-KH7J8J0gAYkm503NJvsh6qw'; // My Campus Map Dev // 'AIzaSyDbNDLJm2D1Y-XZAkDsc1-XbsQ1J_LUud8';
	if (getUrlDomainName() == 'wayfindinguat.polyu.edu.hk' || getUrlDomainName() == 'wwwuat.polyu.edu.hk') {
		mapKey='AIzaSyDiB1BQ2EmaPKjBuSb2hjwTnCq8S9dRMk4';
	} else if (getUrlDomainName() == 'wayfinding.polyu.edu.hk' || getUrlDomainName() == 'www.polyu.edu.hk') {
		mapKey='AIzaSyCLEZOPCPhSLYsJZGgplsjTxswra8w2S7U';
	}

	gLogger.log("DEBUG", "Map Key: "+ mapKey);
	// $.getJSON("https://freegeoip.app/json/", function (data) {
	// 	//console.log(data);
	// 	if (data && data.country_code === 'CN') {	
	// 		window.location.replace("/campus-map/pdf/CampusMap.pdf");
	// 		return;
	// 	}
		var script = document.createElement('script');
		script.type = 'text/javascript';		
		script.src = 'https://maps.googleapis.com/maps/api/js?v=3&key='+mapKey+'&callback=gCampusMap.init';
		if (currentLanguage == 'zh_HK') {
			script.src += '&language=zh-HK';
		} else if (currentLanguage == 'zh_CN') {
			script.src += '&language=zh-CN';
		} else if (currentLanguage == 'en_US') {
			script.src += '&language=en-US';
		}
		script.id = "google-maps-script";
		script.setAttribute('defer','');
		document.body.appendChild(script);
  // }).fail(function() {
	// 	var script = document.createElement('script');
	// 	script.type = 'text/javascript';		
	// 	script.src = 'https://maps.googleapis.com/maps/api/js?v=3&key='+mapKey+'&callback=gCampusMap.init';
	// 	if (currentLanguage == 'zh_HK') {
	// 		script.src += '&language=zh-HK';
	// 	} else if (currentLanguage == 'zh_CN') {
	// 		script.src += '&language=zh-CN';
	// 	} else if (currentLanguage == 'en_US') {
	// 		script.src += '&language=en-US';
	// 	}
	// 	script.id = "google-maps-script";
	// 	script.setAttribute('defer','');
	// 	document.body.appendChild(script);
	// });
}

var gCampusMap = {
	// member variables	
	markerDraggable: false,
	mapsvcobj: null,	
	mapSlidedDown: false,
	directionsvcobj: null,
	projectionsvcobj:null,
	currentPoiCategory: '',
	poiMarkerSize: null,
	originMarker: null,
	originMarkerSize: null,
	originMarkerObj: null,	
	destMarker: null,
	destMakrerSize: null,
	destMarkerObj: null,
	destPath: [],
	destPathObj: [],
	destPathLastObj: null,
	infowindowobj: null,
	lastWayfindingTime: new Date().getTime(),
	searchTimeout: null,
	cache: {},
	markerObj: [],
	markers: {
		AcademicOffice:       academicofficeMarkers = [],
		AdministrativeOffice: administrativeofficeMarkers = [],
		Bank:                 bankMarkers = [],		
		Bookstore:            bookstoreMarkers = [],
		Building:             buildingMarkers = [],
		CarPark:              carparkMarkers = [],
		Canteen:              cateringMarkers = [],
		Clinic:               clinicMarkers = [],
		CoreLocation:         corelocationMarkers = [],
		LectureTheatre:       lecturetheatreMarkers = [],
		Toilet:               toiletMarkers = [],
		AccessibleToilet:     accessibletoiletMarkers = [],
		PublicTransport:	  publictransportMarkers = [],
		Postbox:              postboxMarkers = [],
		WaterStation:         waterstationMarkers = [],
		SportsFacility:       sportsFacilityMarkers = [],
		AED:                  aedMarkers = [],
		ResearchCentre:       researchcenterMarkers = [],
		LactationRoom:        lactationroomMarkers = [],
		PrayerRoom:           prayerroomMarkers = [],
	},
	// member functions
	init: function(resetZoom, resetCenter) {
		gLogger.log("DEBUG", "InitializeCampusMap("+resetZoom+","+resetCenter+") - Enter");
		// initialize parameter
		gCampusMap.markerDraggable = getUrlBooleanParamByName('markerDraggable');				
		// initialize the map
		if (typeof(gCampusMap.mapsvcobj) == "undefined" || gCampusMap.mapsvcobj == null) {
			// determine default zoom level base on device width
			if ($(window).width() < 600) {
				defaultZoomLevel = 17;
			}
			// pre-create path and marker object pool
			gCampusMap.originMakrerSize = new google.maps.Size(40,40);
			gCampusMap.destMakrerSize = new google.maps.Size(40,40);
			gCampusMap.poiMarkerSize = new google.maps.Size(40,40);
			gCampusMap.infowindowobj = new google.maps.InfoWindow({
				content: '',
				//closeBoxMargin: "10px 0px 2px 2px",
				//closeBoxURL: "./images/mapClose.png",
				infoBoxClearance: new google.maps.Size(1, 1),
			});
			for (var i=0 ; i<500; i++) {
				gCampusMap.destPathObj.push(new google.maps.Polyline({
					path: [campusLocations.MTR_A1.getWayPtPos(), campusLocations.MTR_A1.getWayPtPos()],
					geodesic: true,
					strokeColor: '#5c9dde',
					strokeOpacity: 1.0,
					strokeWeight: 7
				}));
			}
			for (var i=0 ; i<200 ; i++) {
				var markerIcon = {
					getIcon: function() {
						return {url: "./img/pin-poi.png", scaledSize: gCampusMap.poiMarkerSize};
					}
				};			
				gCampusMap.markerObj.push(new google.maps.Marker({
					position: campusLocations.MTR_A1.getWayPtPos(),
					draggable: gCampusMap.markerDraggable,
					icon: markerIcon.getIcon(),
					title: "",
					label: "",
					map: null
				}));
			}
			gCampusMap.destPathLastObj = new google.maps.Polyline({
				path: [campusLocations.MTR_A1.getWayPtPos(), campusLocations.MTR_A1.getWayPtPos()],
				geodesic: true,
				strokeColor: '#5c9dde',
				strokeOpacity: 1.0,
				strokeWeight: 7
			});
			// create the google map
			gCampusMap.directionsvcobj = new google.maps.DirectionsService;
			gCampusMap.mapsvcobj = new google.maps.Map(document.getElementById('map-section-campus-map'), {
				styles: [
					{featureType: 'all',             elementType: 'labels',	  stylers: [{visibility: 'off'}]},
					{featureType: 'administrative',  elementType: 'all',      stylers: [{visibility: 'off'}]},
					{featureType: 'landscape',       elementType: 'geometry', stylers: [{visibility: 'on' }]},
					{featureType: 'poi',             elementType: 'geometry', stylers: [{visibility: 'on' }]},
					{featureType: 'transit.station', elementType: 'all',      stylers: [{visibility: 'on' }]},
					{featureType: 'transit.line',    elementType: 'all',      stylers: [{visibility: 'on' }]},
					{featureType: 'road',            elementType: 'all',      stylers: [{visibility: 'on' }]},
					{featureType: 'water',           elementType: 'all',      stylers: [{visibility: 'on' }]},
					{featureType: "water",           elementType: "all",      stylers: [{"saturation": "100"},{"lightness": "-14"}]},
					{featureType: "water",           elementType: "labels",   stylers: [{ "lightness": "12"	}]},
					{featureType: "road",                                     stylers: [{ "visibility": "simplified" }]},
					{featureType: "road.highway",                             stylers: [{ "lightness": 10 }]},
					{featureType: "landscape",                                stylers: [{ "saturation": -100 }]},
				],
				minZoom:minimumZoomLevel, 
				maxZoom: maximumZoomLevel,
				zoom: defaultZoomLevel,
				zoomControlOptions: {
					position: google.maps.ControlPosition.LEFT_BOTTOM
				},	
				center: campusCenterLocation,
				zoomControl: true,
				mapTypeControl: false,
				scaleControl: false,
				streetViewControl: true,
				streetViewControlOptions: {
					position: google.maps.ControlPosition.LEFT_BOTTOM
				},
				rotateControl: false,
				fullscreenControl: true,
				fullscreenControlOptions: {
					position: google.maps.ControlPosition.LEFT_BOTTOM
				},
				provideRouteAlternatives: false,
			});
			// set map header
			var heading = gCampusMap.mapsvcobj.getHeading() || 0;
			gCampusMap.mapsvcobj.setHeading(heading - 270);  
			// add custom control
			gCampusMap._CreateBanner(gCampusMap.mapsvcobj);
			setTimeout(gCampusMap._CreateMenuWrapper, 500, gCampusMap.mapsvcobj);
			// disable all poi click event
			//google.maps.event.addListener(gCampusMap.mapsvcobj, 'click', function (event) {			
			//	event.stop();
			//	return;
			//});
			google.maps.event.addListener(gCampusMap.mapsvcobj, 'dragend', function () {
				//gLogger.log("DEBUG", gCampusMap.mapsvcobj.getCenter().toString());
			});			
			google.maps.event.addListener(gCampusMap.mapsvcobj, 'projection_changed', function() {
				gCampusMap.projectionsvcobj = gCampusMap.mapsvcobj.getProjection();
			}); 			
			// add green map as base map
			var mapBounds_mc = new google.maps.LatLngBounds(
				new google.maps.LatLng(22.30185613, 114.17710626),
				new google.maps.LatLng(22.30817919, 114.18188678));  
			gCampusMap._AddTilesToMap(gCampusMap.mapsvcobj, mapBounds_mc, "tiles/mc");
			var mapBounds_hhb = new google.maps.LatLngBounds(
				new google.maps.LatLng(22.30296524, 114.1843314),
				new google.maps.LatLng(22.30475095, 114.1862153));	
			gCampusMap._AddTilesToMap(gCampusMap.mapsvcobj, mapBounds_hhb, "tiles/hhb");
			var mapBounds_hmt = new google.maps.LatLngBounds(
				new google.maps.LatLng(22.30957279, 114.18353653),
				new google.maps.LatLng(22.31113308, 114.18477653));
			gCampusMap._AddTilesToMap(gCampusMap.mapsvcobj, mapBounds_hmt, "tiles/hmt");
			var mapBounds_shtm = new google.maps.LatLngBounds(
				new google.maps.LatLng(22.30025854, 114.17902731),
				new google.maps.LatLng(22.30192326, 114.18029589));
			gCampusMap._AddTilesToMap(gCampusMap.mapsvcobj, mapBounds_shtm, "tiles/shtm");
			var mapBounds_shtm = new google.maps.LatLngBounds(
				new google.maps.LatLng(22.3121516,  114.16469167),
				new google.maps.LatLng(22.31334493, 114.165702));
			gCampusMap._AddTilesToMap(gCampusMap.mapsvcobj, mapBounds_shtm, "tiles/wk");
			// init pois
			gCampusPois.init(null);			
		} else {
			gCampusMap.ClearAllMarkerInCampusMap();
			if (resetZoom != undefined && resetZoom == true) {
				gCampusMap.mapsvcobj.setZoom(defaultZoomLevel);
			}
			if (resetCenter != undefined && resetCenter == true) {
				gCampusMap.mapsvcobj.setCenter(campusCenterLocation);
			}
		}
		gLogger.log("DEBUG", "InitializeCampusMap() - Exit");
	},
	/***************************************************************
	 * Marker
	 ***************************************************************/
	ClearAllMarkerInCampusMap: function() {
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('AcademicOffice');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('AdministrativeOffice');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('CarPark');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('Canteen');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('Building');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('Bookstore');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('Toilet');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('AccessibleToilet');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('Clinic');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('LectureTheatre');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('CoreLocation');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('PublicTransport');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('Postbox');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('WaterStation');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('SportsFacility');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('AED');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('ResearchCentre');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('LactationRoom');
		gCampusMap.ClearMarkerInCampusMapByPoiCategory('PrayerRoom');
		if (gCampusMap.originMarker != null) {
			gCampusMap.originMarker.setMap(null);
			gCampusMap.originMarker = null;
		}
		if (gCampusMap.destMarker != null) {
			gCampusMap.destMarker.setMap(null);
			gCampusMap.destMarker = null;
		}
		for (var idx=0 ; idx<gCampusMap.destPath.length ; idx++) {
			gCampusMap.destPath[idx].setMap(null);		
		}
		gCampusMap.destPath.length = 0;
		hidePhotoGallery();
	},
	ShowMarkerInCampusMapByPoiName: function (poiCategory, poiName) {
		gLogger.log("DEBUG","ShowMarkerInCampusMapByPoiName("+poiName+")");	
		var markerList = gCampusMap.markers[poiCategory];
		if (markerList.length <= 1) {
			gCampusMap.init(true,true);
			var markerIcon = {
				getIcon: function() {
					return {url: "./img/pin-poi.png", scaledSize: gCampusMap.poiMarkerSize};
				}
			};
			var poiWebVO = gCampusPois.getPoiWebVOByPoiName(poiCategory,poiName);
			gCampusMap.markerObj[0].setPosition(poiWebVO.getMapMarkerLatLng());
			gCampusMap.markerObj[0].setTitle(poiWebVO.getPoiName());
			gCampusMap.markerObj[0].setIcon(markerIcon.getIcon());
			gCampusMap.markerObj[0].setMap(gCampusMap.mapsvcobj);
			gCampusMap.markerObj[0].poiWebVO = undefined;
			poiWebVO.markerObject = gCampusMap.markerObj[0];
			google.maps.event.addListener(gCampusMap.markerObj[0], 'click', (function(marker, i) {
				return function() {
					gCampusMap.ShowInfoWindowWithMarkerClick(poiWebVO,gCampusMap.markerObj[0]);						
				}
			}) (gCampusMap.markerObj[0], 0));
			markerList.push(gCampusMap.markerObj[0]);
		}
	},	
	ShowMarkerInCampusMapByPoiCategory: function (poiCategory) {
		gLogger.log("DEBUG","ShowMarkerInCampusMapByPoiCategory("+poiCategory+")");		
		var markerList = gCampusMap.markers[poiCategory];
		gCampusMap.init(true,true);
		if ( markerList.length == 0) {
			var markerIcon = {
				getIcon: function() {
					return {url: "./img/pin-poi.png", scaledSize: gCampusMap.poiMarkerSize};
				}
			};
			//this.ClearAllMarkerInCampusMap();
			poiWebVOs = gCampusPois.listPoiWebVOsByPoiType(poiCategory);
			for(var i=0 ; i<poiWebVOs.length  ; i++) {
				gCampusMap.markerObj[i].setPosition(poiWebVOs[i].getMapMarkerLatLng());
				gCampusMap.markerObj[i].setTitle(poiWebVOs[i].getPoiName());
				gCampusMap.markerObj[i].setIcon(markerIcon.getIcon());
				gCampusMap.markerObj[i].setMap(gCampusMap.mapsvcobj);
				gCampusMap.markerObj[i].poiWebVO = undefined;
				poiWebVOs[i].markerObject = gCampusMap.markerObj[i];
				google.maps.event.addListener(gCampusMap.markerObj[i], 'click', (function(marker, i) {
					return function() {
						gCampusMap.ShowInfoWindowWithMarkerClick(poiWebVOs[i],gCampusMap.markerObj[i]);						
					}
				}) (gCampusMap.markerObj[i], i));
				markerList.push(gCampusMap.markerObj[i]);
			}
		}
	},
	ClearMarkerInCampusMapByPoiCategory: function (poiCategory) {
		gLogger.log("DEBUG","ClearMarkerInCampusMapByPoiCategory("+poiCategory+")");		
		if (gCampusMap.infowindowobj != undefined) {
			gCampusMap.infowindowobj.close();
		}
		var markerList = gCampusMap.markers[poiCategory];
		if ( markerList.length > 0) {
			var i;
			for (i = 0; i < markerList.length; i++) { 
				markerList[i].setMap(null);
			}
			markerList.splice(0,markerList.length)
		}		
	},
	/***************************************************************
	 * Info Window
	 ***************************************************************/
	ShowInfoWindowWithUrlParam: function(poiCategory, poiName){
		gLogger.log("DEBUG","ShowInfoWindowWithMenuClick("+poiName+")");
		var poiWebVO = gCampusPois.getPoiWebVOByPoiName(poiCategory, poiName);
		gCampusMap.ClearAllMarkerInCampusMap();
		gCampusMap.ShowMarkerInCampusMapByPoiName(poiCategory, poiName);
		gCampusMap.ShowInfoWindowWithMarkerClick(poiWebVO, poiWebVO.markerObject);
	},
	ShowInfoWindowWithPhotoGallery: function(poiCategory, poiName){
		gLogger.log("DEBUG","ShowInfoWindowWithPhotoGallery("+poiName+")");
		var poiWebVO = gCampusPois.getPoiWebVOByPoiName(poiCategory, poiName);
		//gCampusMap.ClearAllMarkerInCampusMap();
		gCampusMap.ShowMarkerInCampusMapByPoiName(poiCategory, poiName);
		gCampusMap.ShowInfoWindowWithMarkerClick(poiWebVO, poiWebVO.markerObject);
		//gCampusMap._ResetRootMenu();
	},
	ShowInfoWindowWithMenuClick: function(poiCategory, poiName){
		gLogger.log("DEBUG","ShowInfoWindowWithMenuClick("+poiName+")");
		var poiWebVO = gCampusPois.getPoiWebVOByPoiName(poiCategory, poiName);
		gCampusMap.ClearAllMarkerInCampusMap();
		gCampusMap.ShowMarkerInCampusMapByPoiName(poiCategory, poiName);
		gCampusMap.ShowInfoWindowWithMarkerClick(poiWebVO, poiWebVO.markerObject);
		gCampusMap._ResetRootMenu();
	},
	ShowInfoWindowWithMarkerClick: function(poiWebVO, marker) {
		gLogger.log("DEBUG","ShowInfoWindowWithMarkerClick("+poiWebVO.getPoiName()+","+poiWebVO.getPoiType()+")");		
		var directionImg = (getUrlStringParamByName('direction') != 'api') ? 'poi-direction-google.png' : 'poi-direction-api.png';
		var contentString = '<div id="info-window" class="info-window">'+
			'<h5 id="info-window-poi-heading">'+poiWebVO.getPoiName()+'</h5>'+
			'<div id="info-window-poi-content">'+
				'<div style="display:flex"><img class="info-window-poi-addr-img" draggable="false" src="./img/pin-poi-loc.png"/><span class="info-window-poi-addr-txt">'+ poiWebVO.getPoiAddr() + '</span></div>' +
				((poiWebVO.getPoiType() == 'Canteen' || poiWebVO.getPoiType() == 'Clinic') ? '<div style="display:flex"><img class="info-window-poi-open-hour-img" draggable="false" src="./img/pin-poi-open-hour.png"/><span class="info-window-poi-open-hour-txt">'+ poiWebVO.getPoiOpeningHour() + '</span></div>' : '') +
				((poiWebVO.getPoiType() == 'SportsFacility') ? '<div style="display:flex"><img class="info-window-poi-sports-facility-img" draggable="false" src="./img/sports.png"/><span class="info-window-poi-sports-facility-txt">'+ poiWebVO.getPoiSportsFacilities() + '</span></div>' : '') +
				((poiWebVO.getPoiImageUrl() != null) ? '<img class="info-window-poi-img" draggable="false" src="'+poiWebVO.getPoiImageUrl()+'"/>' : '')+
				((poiWebVO.getPoiType() == 'AED' && poiWebVO.getReferenceUrl() != null) ? '<img class="info-window-poi-img" draggable="false" src="'+poiWebVO.getReferenceUrl()+'"/>' : '')+
				'<br/>' + 
				'<div class="info-window-nav-pane">' +
					((getMobileOS() != 'unknown' && navigator.geolocation) ? '<div class="info-window-nav-btn" onclick="gCampusMap.DoWayfinding('+"'"+poiWebVO.getPoiType()+"','"+poiWebVO.getPoiNameByLang('en_US')+"'"+');"><img class="info-window-nav-btn-img" draggable="false" src="./img/poi-direction-api.png"/><span class="info-window-nav-txt">'+getLabelByLang("LBL0023", currentLanguage)+'</span></div>' : '') +
					'<div class="info-window-nav-btn" onclick="gCampusMap.DoRedirectGoogleMap('+"'"+poiWebVO.getPoiType()+"','"+poiWebVO.getPoiNameByLang('en_US')+"'"+');"><img class="info-window-nav-btn-img" draggable="false" src="./img/poi-direction-google.png"/><span class="info-window-nav-txt">'+getLabelByLang("LBL0020", currentLanguage)+'</span></div>' +
					'<div id="info-window-copy-url-btn" class="info-window-nav-btn" onclick="gCampusMap.DoCopyURL('+"'"+poiWebVO.getPoiObjectId()+"'"+');"><img class="info-window-nav-btn-img" draggable="false" src="./img/poi-link.png"/><span class="info-window-nav-txt">&nbsp;'+getLabelByLang("LBL0021", currentLanguage)+'</span><input type="hidden" value="" id="poi-url-value"><span class="tooltiptext"><i class="fa">&#xf00c;</i>&nbsp;'+getLabelByLang("LBL0022", currentLanguage)+'</span></div>' +
//					((getMobileOS() == 'unknown') ? '<div id="info-window-copy-url-btn" class="info-window-nav-btn" onclick="gCampusMap.DoCopyURL('+"'"+poiWebVO.getPoiObjectId()+"'"+');"><img class="info-window-nav-btn-img" draggable="false" src="./img/poi-link.png"/><span class="info-window-nav-txt">&nbsp;'+getLabelByLang("LBL0021", currentLanguage)+'</span><input type="hidden" value="" id="poi-url-value"><span class="tooltiptext"><i class="fa">&#xf00c;</i>&nbsp;'+getLabelByLang("LBL0022", currentLanguage)+'</span></div>' : '') +
//					((getMobileOS() != 'unknown' ) ? '<div class="info-window-nav-btn" onclick="window.location='+"'../mobile/polyuway.html?cat=POIs&id="+poiWebVO.getPoiObjectId()+"'"+'"><img class="info-window-nav-btn-img" draggable="false" src="./img/polyuway.png"/><span class="info-window-nav-txt">POLY:U:WAY</span></div>' : '')+
				'</div>' +
			'</div></div>';
		if (gCampusMap.infowindowobj != undefined) {
			gCampusMap.infowindowobj.close();
			gCampusMap.infowindowobj.setContent(contentString);
			gCampusMap.infowindowobj.open(gCampusMap.mapsvcobj, marker);	
			gCampusMap.mapsvcobj.panTo(marker.getPosition());
		}
	},
	/***************************************************************
	 * Wayfinding
	 ***************************************************************/
	DoCopyURL: function(poiObjectId) {
		gLogger.log("DEBUG", "DoCopyURL(" + poiObjectId + ") - Enter");
		var copyText = document.getElementById("poi-url-value");
		copyText.setAttribute('type', 'text')
		copyText.value = getUrl() + "?lang=" + currentLanguage + "&locid=" + poiObjectId;
		copyText.select();
		copyText.setSelectionRange(0, 99999);
		document.execCommand("copy");
		copyText.setAttribute('type', 'hidden')
		$('#info-window-copy-url-btn .tooltiptext').fadeIn('fast', function() {
			$(this).css('display','block');
		 });
		setTimeout(function(){
			$('#info-window-copy-url-btn .tooltiptext').fadeOut('fast', function() {
				$(this).css('display','none');
			 });
		}, 1000);
		gLogger.log("DEBUG", "DoCopyURL(" + poiObjectId + ") - Copied: " + copyText.value);
	},
	DoRedirectGoogleMap: function(poiCategory, poiName) {
		gLogger.log("DEBUG", "DoRedirectGoogleMap(" + poiCategory + "," + poiName + ") - Enter");
		var poiWebVO = gCampusPois.getPoiWebVOByPoiName(poiCategory, poiName);
		if (poiWebVO != null) {
			window.open("https://www.google.com/maps/dir/?api=1&travelmode=walking&destination="+poiWebVO.getWayPtLatLng().lat+","+poiWebVO.getWayPtLatLng().lng);
		}
	},
	DoWayfinding: function(poiCategory, poiName, origin) {
		if (origin == null) {
			navigator.geolocation.getCurrentPosition(
				function(position){
					gCampusMap.DoWayfinding(poiCategory, poiName, {lat: position.coords.latitude, lng: position.coords.longitude});
				},
				function(error) {
					if (error.code == error.PERMISSION_DENIED) {
						var modelmessage = document.getElementById("modal-message");
						modelmessage.innerHTML = getLabelByCurrLang("LBL0013");
						var modalform = document.getElementById("modal-form");
						modalform.style.display = "block";
					} else {
						var modelmessage = document.getElementById("modal-message");
						modelmessage.innerHTML = getLabelByCurrLang("LBL0014");
						var modalform = document.getElementById("modal-form");
						modalform.style.display = "block";
					}
				});
			return;
		}
		gLogger.log("DEBUG", "DoWayfinding(" + poiCategory + "," + poiName + "," + JSON.stringify(origin) + ") - Enter");
		var poiWebVO = gCampusPois.getPoiWebVOByPoiName(poiCategory, poiName);
		var destination = poiWebVO;
		if (poiWebVO != null && gCampusMap.cache[poiWebVO.getPoiObjectId()] != undefined) {
			var response = gCampusMap.cache[poiWebVO.getPoiObjectId()];
			gLogger.log("DEBUG", "Wayfinding Result From Cache --->", response);
			gCampusMap.cache[poiWebVO.getPoiObjectId()] = response;
			gCampusMap.ShowWayfindingResult(poiWebVO, origin, destination, response);
		} else if (poiWebVO != null) {
			var timeDiff = new Date().getTime() - gCampusMap.lastWayfindingTime;
			if (timeDiff < 500) {
				gLogger.log("DEBUG", "Wayfinding To Too Many Click...Retry ("+timeDiff+")");
				setTimeout(gCampusMap.DoWayfinding, 500, poiCategory, poiName);
			} // No wayfinding when click too fast
			else {
				gCampusMap.directionsvcobj.route({
					origin: origin,
					destination: destination.getWayPtLatLng(),
					waypoints: destination.getPoiDestWayPoints(),
					travelMode: 'WALKING',
					provideRouteAlternatives: false
				}, function(response, status) {
					if (status === 'OK') {
						gLogger.log("DEBUG", "Wayfinding Result From Google --->", response);					
						gCampusMap.cache[poiWebVO.getPoiObjectId()] = response;					
						gCampusMap.lastWayfindingTime = new Date().getTime();
						gCampusMap.ShowWayfindingResult(poiWebVO, origin, destination, response);
					} else if (status === 'OVER_QUERY_LIMIT') {
						gLogger.log("DEBUG", "Wayfinding Over Limit...Retry");
						setTimeout(gCampusMap.DoWayfinding, 1000, poiCategory, poiName);
					} else {
						gLogger.log("DEBUG", "Wayfinding Error");
						gPanelOfErrorMessage.open('LBL0043', status);
					}
				});
			}
		} else {
			gPanelOfErrorMessage.open('LBL0042', null);
		}
		gLogger.log("DEBUG", "DoWayfinding() - Exit");
	},
	ShowWayfindingResult: function(poiWebVO, origin, destination, response) {
		gCampusMap.init(false,false);
		gCampusMap._ResetRootMenu();
		// 1. clear previous wayfinding path to destination if any		
		for (var idx=0 ; idx<gCampusMap.destPath.length ; idx++) {
			gCampusMap.destPath[idx].setMap(null);
		}
		gCampusMap.destPath.length = 0;
		// 2a. draw the origin marker
		if (gCampusMap.originMarker != null) {
			gCampusMap.originMarker.setMap(null);
			gCampusMap.originMarker = null;
		}
		if (gCampusMap.originMarkerObj == null) {
			gCampusMap.originMarkerObj = new google.maps.Marker({
				position: origin,
				draggable: gCampusMap.markerDraggable,
				icon: {url: "./img/pin-origin.png", scaledSize: gCampusMap.originMakrerSize},
				title: "",
				label: "",
				map: gCampusMap.mapsvcobj
			});			
		} else {
			gCampusMap.originMarkerObj.setPosition(origin);
			gCampusMap.originMarkerObj.setIcon({url: "./img/pin-origin.png", scaledSize: gCampusMap.originMakrerSize});
			gCampusMap.originMarkerObj.setMap(gCampusMap.mapsvcobj);			
		}
		gCampusMap.originMarker = gCampusMap.originMarkerObj;
		// 2b. draw the destination marker		
		if (gCampusMap.destMarker != null) {
			gCampusMap.destMarker.setMap(null);
			gCampusMap.destMarker = null;
		}
		if (gCampusMap.destMarkerObj == null) {
			gCampusMap.destMarkerObj = new google.maps.Marker({
				position: destination.getDestMarkerLatLng(),
				draggable: gCampusMap.markerDraggable,
				icon: {url: "./img/pin-poi.png", scaledSize: gCampusMap.destMakrerSize},
				title: poiWebVO.getPoiName(),
				label: "",
				map: gCampusMap.mapsvcobj
			});			
		} else {
			gCampusMap.destMarkerObj.setPosition(destination.getDestMarkerLatLng());
			gCampusMap.destMarkerObj.setIcon({url: "./img/pin-poi.png", scaledSize: gCampusMap.destMakrerSize});
			gCampusMap.destMarkerObj.setTitle(poiWebVO.getPoiName());
			gCampusMap.destMarkerObj.setMap(gCampusMap.mapsvcobj);			
		}
		gCampusMap.destMarker = gCampusMap.destMarkerObj;
		// 3. draw the path from origin to destination
		for (var idx=0 ; idx<response.routes[0].overview_path.length-1 ; idx++) {
			gCampusMap.destPathObj[idx].setPath([idx==0 ? origin : response.routes[0].overview_path[idx],response.routes[0].overview_path[idx+1]]);
			gCampusMap.destPathObj[idx].setMap(gCampusMap.mapsvcobj);
			gCampusMap.destPath.push(gCampusMap.destPathObj[idx]);
		}
		gCampusMap.destPathLastObj.setPath([response.routes[0].overview_path[idx],destination.getDestMarkerLatLng()]);
		gCampusMap.destPathLastObj.setMap(gCampusMap.mapsvcobj);
		gCampusMap.destPath.push(gCampusMap.destPathLastObj);
		// 4. show info window
		//gCampusMap.ShowInfoWindowWithMarkerClick(poiWebVO, gCampusMap.destMarker);
		// 5. zoom to fit all markers in map
		var bounds = new google.maps.LatLngBounds();
		bounds.extend(origin);
		bounds.extend(gCampusMap.destMarker.getPosition());
		gCampusMap.mapsvcobj.fitBounds(bounds);
		google.maps.event.addListener(gCampusMap.destMarker, 'dragend', function() {
			gLogger.log("DEBUG", gCampusMap.destMarker.getPosition().toString());
		});	
		// 6. call to backend to record wayfinding event
		var xmlhttp = new XMLHttpRequest();	
		xmlhttp.onreadystatechange = function() {};
		xmlhttp.open("GET", "../public-data/DirectionSvc:"+poiWebVO.getPoiNameByLang('en_US').replace(/ /g,''), true);
		xmlhttp.send();
	},
	/***************************************************************
	 * Helper Function
	 ***************************************************************/
	_UpdateSearchResultWrapper: function(searchCriteria) {
		if (gCampusMap.searchTimeout != null) {
			clearTimeout(gCampusMap.searchTimeout);
		}
		gCampusMap.searchTimeout = setTimeout(gCampusMap._UpdateSearchResult, 300, searchCriteria);
	},
	_UpdateSearchResult: function(searchCriteria) {
		if (searchCriteria != null && searchCriteria.length > 0 && trim(searchCriteria).length > 0) {
			gCampusMap._HideAllSubMenuItem();
			var menuItems = document.getElementsByClassName('menu-item-div');
			for (var i=0 ; i<menuItems.length ; i++) {
				menuItems[i].style.display = 'none';
			}
			var searchResultDiv = document.getElementById('menu-item-searchresult');
			var serachResulPoiWebVOs = gCampusPois.listPoiWebVOsByKeyword(trim(searchCriteria));
			var searchResultHtml = "";
			for (var i=0 ; i<serachResulPoiWebVOs.length ; i++) {
				searchResultHtml = searchResultHtml + '<a class="menu-item-poi" onclick="gCampusMap.ShowInfoWindowWithMenuClick('+"'"+serachResulPoiWebVOs[i].getPoiType()+"','"+serachResulPoiWebVOs[i].getPoiNameByLang('en_US')+"');"+'"><span class="menu-item-poi-name">'+serachResulPoiWebVOs[i].getPoiName()+'</span></a>';
			}
			searchResultDiv.innerHTML = searchResultHtml;
			searchResultDiv.style.display = 'block';
		} else {
			var searchResult = document.getElementById('menu-item-searchresult');
			searchResult.style.display = 'none';
			var menuItems = document.getElementsByClassName('menu-item-div');
			for (var i=0 ; i<menuItems.length ; i++) {
				menuItems[i].style.display = 'flex';
			}
		}
	},
	_ClearSearchResult: function() {
		gCampusMap._UpdateSearchResult('');
		document.getElementById('menu-item-searchbox-input').value = '';		
	},
	_ToggleMapMarker: function(source, poiCategory) {
		if (source.checked) {
			var checkboxes = document.getElementsByClassName('menu-item-chkbox');
			for (var i=0 ; i<checkboxes.length ; i++) {
				if (checkboxes[i].id != source.id && checkboxes[i].checked) {
					checkboxes[i].checked = false;
				}
			}
			gCampusMap.ShowMarkerInCampusMapByPoiCategory(poiCategory);
			var rootitem = document.getElementById('menu-item-root');
			rootitem.style.display = (rootitem.style.display == 'block') ? 'none' : 'block';
			gCampusMap.currentPoiCategory = poiCategory;
			showPhotoGallery(poiCategory);
		} else {
			gCampusMap.currentPoiCategory = '';
			hidePhotoGallery();
			gCampusMap.ClearMarkerInCampusMapByPoiCategory(poiCategory);
		}
	},
	_HideAllSubMenuItem: function(source) {
		var items = document.getElementsByClassName('menu-item');
		for (var i=0 ; i<items.length ; i++) {
			if (items[i].id != 'menu-item-root' && items[i].style.display == 'block') {
				items[i].style.display = 'none';				
				var sourceSibling = items[i].previousSibling.childNodes[0];
				for (var j=0 ; j<sourceSibling.childNodes.length ; j++) {
					var nodeName = sourceSibling.childNodes[j].nodeName;
					var nodeClass = sourceSibling.childNodes[j].className;
					if (nodeName == 'SPAN' && (nodeClass == 'menu-icon glyphicon glyphicon-triangle-right' || nodeClass == 'menu-icon glyphicon glyphicon-triangle-bottom')) {
						sourceSibling.childNodes[j].className = (items[i].style.display == 'block') ? 'menu-icon glyphicon glyphicon-triangle-bottom' : 'menu-icon glyphicon glyphicon-triangle-right';
					}
				}		
			}
		}
	},	
	_ZoomInMenuItem: function() {
		var currfontsize = $('.menu-item').css('font-size');
		if (currfontsize == '10px') {
			$('.menu-item').css('width','280px');
			$('.menu-item').css('max-width','280px');
			$('.menu-item').css('font-size','12px');
			$('.menu-item-option').css('font-size','14px');
			$('.menu-item-fontp').css('font-size','14px');
			$('.menu-item-fontm').css('font-size','14px');
			$('.menu-item-fontm').css('color','#ffffff');
		} else if (currfontsize == '12px') {
			$('.menu-item').css('width','290px');
			$('.menu-item').css('max-width','290px');
			$('.menu-item').css('font-size','14px');
			$('.menu-item-option').css('font-size','16px');
			$('.menu-item-fontp').css('font-size','16px');
			$('.menu-item-fontm').css('font-size','16px');
			$('.menu-item-fontp').css('color','#f7f7f74f');
		}
	},
	_ZoomOutMenuItem: function() {
		var currfontsize = $('.menu-item').css('font-size');
		if (currfontsize == '12px') {
			$('.menu-item').css('width','280px');
			$('.menu-item').css('max-width','280px');
			$('.menu-item').css('font-size','10px');
			$('.menu-item-option').css('font-size','12px');
			$('.menu-item-fontp').css('font-size','12px');
			$('.menu-item-fontm').css('font-size','12px');
			$('.menu-item-fontm').css('color','#f7f7f74f');
		} else if (currfontsize == '14px') {
			$('.menu-item').css('width','280px');
			$('.menu-item').css('max-width','280px');
			$('.menu-item').css('font-size','12px');
			$('.menu-item-option').css('font-size','14px');
			$('.menu-item-fontp').css('font-size','14px');
			$('.menu-item-fontm').css('font-size','14px');
			$('.menu-item-fontp').css('color','#ffffff');
		}
	},	
	_ResetRootMenu: function() {		
		gLogger.log('DEBUG','_ResetRootMenu()');
		var rootitem = document.getElementById('menu-item-root');
		if (rootitem.style.display == 'block') {
			var rootbtn = document.getElementById('menu-root-button');			
			gCampusMap._HideAllSubMenuItem(rootbtn);
			gCampusMap._ToggleMenuItem(rootbtn,'menu-item-root');
		}
		// clear all checkbox
		var checkboxes = document.getElementsByClassName('menu-item-chkbox');
		for (var i=0 ; i<checkboxes.length ; i++) {
			checkboxes[i].checked = false;
		}
	},	
	_ToggleMenuItem: function(source,itemid) {		
		gLogger.log('DEBUG','_ToggleMenuItem('+itemid+')',source);
		// toggle selected menu item
		var menuMaxHeightLv0 = ($(window).height() - 200) + "px"; 
		var menuMaxHeightLv1 = ($(window).height() - 430) + "px"; 
		if ($(window).width() < 600) {
			menuMaxHeightLv0 = ($(window).height() - 160) + "px"; 
			menuMaxHeightLv1 = ($(window).height() - 390) + "px"; 
		}
		$(".menu-item-searchresult").css("max-height", menuMaxHeightLv0);
		$(".menu-item-lvl1").css("max-height", menuMaxHeightLv1);
		var item = document.getElementById(itemid);			
		item.style.display = (item.style.display == 'block') ? 'none' : 'block';		
		for (var i=0 ; i<source.childNodes.length ; i++) {
			var nodeName = source.childNodes[i].nodeName;
			var nodeClass = source.childNodes[i].className;
			if (nodeName == 'SPAN' && (nodeClass == 'menu-icon glyphicon glyphicon-triangle-right' || nodeClass == 'menu-icon glyphicon glyphicon-triangle-bottom')) {
				source.childNodes[i].className = (item.style.display == 'block') ? 'menu-icon glyphicon glyphicon-triangle-bottom' : 'menu-icon glyphicon glyphicon-triangle-right';
			}
		}
		if (itemid == 'menu-item-root') {
			gCampusMap._ClearSearchResult();
			//document.getElementById('menu-item-searchbox-input').focus();
		} else {
			// hide other menu item
			var items = document.getElementsByClassName('menu-item');
			for (var i=0 ; i<items.length ; i++) {
				if ((itemid != 'menu-item-canteen' && itemid != 'menu-item-lecturetheatre' && itemid != 'menu-item-clinic' && itemid != 'menu-item-toilet' && itemid != 'menu-item-sportsfacility' && itemid != 'menu-item-waterstation' && itemid != 'menu-item-aed' && itemid != 'menu-item-researchcentre'  && itemid != 'menu-item-lactationroom'  && itemid != 'menu-item-prayerroom' && items[i].id != 'menu-item-root' && items[i].id != itemid && items[i].style.display == 'block') || 
						((itemid == 'menu-item-canteen' || itemid == 'menu-item-lecturetheatre' || itemid == 'menu-item-clinic' || itemid == 'menu-item-toilet' || itemid == 'menu-item-sportsfacility' || itemid == 'menu-item-waterstation' || itemid == 'menu-item-aed' || itemid == 'menu-item-researchcentre') && items[i].id != 'menu-item-amenities' && items[i].id != 'menu-item-root' && items[i].id != itemid && items[i].style.display == 'block')) {
					items[i].style.display = 'none';
					var sourceSibling = items[i].previousSibling.childNodes[0];
					for (var j=0 ; j<sourceSibling.childNodes.length ; j++) {
						var nodeName = sourceSibling.childNodes[j].nodeName;
						var nodeClass = sourceSibling.childNodes[j].className;
						if (nodeName == 'SPAN' && (nodeClass == 'menu-icon glyphicon glyphicon-triangle-right' || nodeClass == 'menu-icon glyphicon glyphicon-triangle-bottom')) {
							sourceSibling.childNodes[j].className = (items[i].style.display == 'block') ? 'menu-icon glyphicon glyphicon-triangle-bottom' : 'menu-icon glyphicon glyphicon-triangle-right';
						}
					}		
				}
			}
		}
	},	
	_CreateBanner: function(mymap) {

		// calculate logo padding and size depending on screen width
		var logoPadding = '40px';
		var logoSize = '80px';
		if ($(window).width() < 600) {
			logoPadding = '20px';
			logoSize = '50px';
		}

		// Creating divs & styles for banner
		var controlDiv = document.createElement('div');	
		controlDiv.style.paddingTop = logoPadding;
		controlDiv.style.paddingLeft = logoPadding;
		//controlDiv.style.paddingRight = logoPadding;

		// control wrapper
		var controlWrapper = document.createElement('div');
		controlWrapper.style.backgroundColor = 'rgba(255,255,255,0.0)';
		controlWrapper.style.textAlign = 'left';
		controlWrapper.style.display = 'flex';
		controlWrapper.style.flexDirection = 'row nowrap';
		//controlWrapper.style.flexDirection = 'column';
		controlWrapper.style.verticalAlign = 'top';
		controlDiv.appendChild(controlWrapper);

		// banner
		var bannerDiv = document.createElement('div');
		bannerDiv.id = 'campus-map-banner';
		bannerDiv.style.width = logoSize; 
		bannerDiv.style.height = logoSize;
		bannerDiv.style.marginLeft = '0px';
		bannerDiv.style.marginTop = '0px';
		bannerDiv.style.background = 'url(./img/logo.png)';  
		bannerDiv.style.backgroundSize = "cover";
		bannerDiv.style.cursor = 'pointer';
		bannerDiv.onclick = function () { window.open("https://www.polyu.edu.hk"); };
		controlWrapper.appendChild(bannerDiv);

		// alert
		//var alertDiv = document.createElement('div');
		//alertDiv.id = 'campus-map-alert';
		//alertDiv.className = 'alert';
		//alertDiv.style.marginLeft = '0px';
		//alertDiv.style.marginTop = '20px';
		//alertDiv.innerHTML = '<span class="alert-closebtn" onclick="this.parentElement.style.display='+"'none'"+';">&times;</span> <strong>Announcement</strong><br/>The University has stepped up security controls on campus. Please enter via main entrance in Chatham Road South that near Core A or Block Y.</div>';
		//controlWrapper.appendChild(alertDiv);

		controlDiv.index = 1;
		mymap.controls[google.maps.ControlPosition.TOP_LEFT].push(controlDiv);

	},
	_CreateMenuWrapper: function(mymap) {
		if (gCampusPois.inited == true) {			
			gCampusMap._CreateMenu(mymap);
			if (getUrlStringParamByName('loc') != null && getUrlStringParamByName('loc') != "") {
				var poiWebVO = gCampusPois.getPoiWebVOByPoiLocCode('Building',getUrlStringParamByName('loc'));
				if (poiWebVO != null) {
					gCampusMap.ShowInfoWindowWithUrlParam(poiWebVO.getPoiType(), poiWebVO.getPoiNameByLang('en_US'));
				}
			}
			if (getUrlStringParamByName('locid') != null && getUrlStringParamByName('locid') != "") {
				var poiCategories = gCampusPois.listPoiCategory();
				poiCategories.forEach(function(poiType, index) {
					var poiWebVO = gCampusPois.getPoiWebVOByPoiObjectId(poiType,getUrlStringParamByName('locid'));
					if (poiWebVO != null) {
						gCampusMap.ShowInfoWindowWithUrlParam(poiWebVO.getPoiType(), poiWebVO.getPoiNameByLang('en_US'));
						return;
					}
				});
			}
		} else {
			gLogger.log("INFO", 'Await POI Data Init CP2');
			setTimeout(gCampusMap._CreateMenuWrapper, 1000, mymap);
		}
	},	
	_CreateMenu: function(mymap) {

		// prepare poi html content
		var poiCategory = gCampusPois.listPoiCategory();
		var poiHtml = {};
		for (var i=0 ; i<poiCategory.length ; i++) {
			poiWebVOs = gCampusPois.listPoiWebVOsByPoiType(poiCategory[i]);
			poiHtml[poiCategory[i]] = '';
			for (var j=0 ; j<poiWebVOs.length ; j++) {
				if (poiCategory[i] == 'WaterStation') {
					poiHtml[poiCategory[i]] = poiHtml[poiCategory[i]] +'<a class="menu-item-poi" onclick="gCampusMap.ShowInfoWindowWithMenuClick('+"'"+poiCategory[i]+"','"+poiWebVOs[j].getPoiNameByLang('en_US')+"');"+'"><span class="menu-item-poi-name menu-item-waterstation-name">'+poiWebVOs[j].getPoiName()+'</span>&nbsp;<img src="./img/cold.png"/>'+ (poiWebVOs[j].isHotWaterStation() ? '<img src="./img/hot.png"/>' : '') +'</a>';
				} else {
					poiHtml[poiCategory[i]] = poiHtml[poiCategory[i]] +'<a class="menu-item-poi" onclick="gCampusMap.ShowInfoWindowWithMenuClick('+"'"+poiCategory[i]+"','"+poiWebVOs[j].getPoiNameByLang('en_US')+"');"+'"><span class="menu-item-poi-name">'+poiWebVOs[j].getPoiName()+'</span></a>';
				}
			}
		}

		// calculate menu padding depending on screen width
		var menuPaddingTop = '40px';
		var menuPaddingRight = '15px';
		if ($(window).width() < 600) {
			menuPaddingTop = '20px';
			menuPaddingRight = '10px';
		}

		// Creating divs & styles for menu
		var controlDiv = document.createElement('div');	
		controlDiv.id = 'menu';
		controlDiv.style.paddingTop = menuPaddingTop;
		controlDiv.style.paddingRight = menuPaddingRight;
		controlDiv.style.backgroundColor = 'rgba(255,255,255,0.0)';
		controlDiv.index = 1;
		controlDiv.innerHTML=
		'<button id="menu-root-button" class="menu-root-button" type="button" onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-root'"+')" >'+
			'<span class="glyphicon glyphicon-th" style="top:0px !important;"></span>'+
		'</button>'+
		'<div id="menu-item-root" class="menu-item menu-item-lvl0">'+
			'<div style="display:flex; justify-content:flex-end; background:#a02337; padding-top: 5px; margin-bottom:5px;"><div id="menu-language"><span class="menu-item-option-en-us" onclick="window.location='+"'./index.html?lang=en_US'"+'">ENG</span> | <span class="menu-item-option-zh-hk" onclick="window.location='+"'./index.html?lang=zh_HK'"+'">繁體</span> | <span class="menu-item-option-zh-cn" onclick="window.location='+"'./index.html?lang=zh_CN'"+'">简体</span></div>&nbsp;&nbsp;&nbsp;<div style="box-shadow: -1px 0 0 #ffffff; margin-top:3px; margin-bottom:3px;">&nbsp;</div>&nbsp;&nbsp;<div id="menu-font-size"><span class="menu-item-fontp" onclick="gCampusMap._ZoomInMenuItem();">A+</span>&nbsp;&nbsp;<span class="menu-item-fontm" onclick="gCampusMap._ZoomOutMenuItem();">A-</span></div>&nbsp;&nbsp;<div style="box-shadow: -1px 0 0 #ffffff; margin-top:3px; margin-bottom:3px;">&nbsp;</div>&nbsp;&nbsp;<div id="menu-print"><a target="popup" onclick="window.open('+"'"+'/campus-map/pdf/CampusMap.pdf'+"','"+'popup'+"'"+'); return false;" style="padding:0px"><img style="height:20px; padding-right:6px; padding-bottom:4px;" src="./img/printer.png"/></a></div></div>'+
			'<div id="menu-item-searchbox" style="margin-bottom:5px;"><input id="menu-item-searchbox-input" class="menu-item-searchbox-input" type="text" placeholder="'+getLabelByCurrLang("LBL0011")+'" title="'+getLabelByCurrLang("LBL0012")+'" autocomplete="off" onkeyup="gCampusMap._UpdateSearchResultWrapper(document.getElementById('+"'"+'menu-item-searchbox-input'+"'"+').value);"/><button type="reset" class="menu-item-searchbox-btn" onclick="gCampusMap._ClearSearchResult();"><span class="glyphicon glyphicon-remove"></span></button></div>'+
			'<div id="menu-item-searchresult" class="menu-item menu-item-searchresult" style="display:none"></div>' + 
			'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-academic-office'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0001")+'</a><input type="checkbox" id="menu-item-chkbox-academic-office" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'AcademicOffice'"+')"></input></div>'+
				'<div id="menu-item-academic-office" class="menu-item menu-item-lvl1">'+
					poiHtml['AcademicOffice'] +
				'</div>'+
			'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-admin-office'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0002")+'</a><input type="checkbox" id="menu-item-chkbox-admin-office" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'AdministrativeOffice'"+')"></input></div>'+
				'<div id="menu-item-admin-office" class="menu-item menu-item-lvl1">'+
					poiHtml['AdministrativeOffice'] +
				'</div>'+
			'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-building'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0003")+'</a><input type="checkbox" id="menu-item-chkbox-building" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'Building'"+')"></input></div>'+
				'<div id="menu-item-building" class="menu-item menu-item-lvl1">'+
					poiHtml['Building'] +
				'</div>'+
			'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-corelocation'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0004")+'</a><input type="checkbox" id="menu-item-chkbox-corelocation" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'CoreLocation'"+')"></input></div>'+
				'<div id="menu-item-corelocation" class="menu-item menu-item-lvl1">'+
					poiHtml['CoreLocation'] +
				'</div>'+
			'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-amenities'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0005")+'</a></div>'+
				'<div id="menu-item-amenities" class="menu-item menu-item-lvl1">'+
					'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-aed'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0019")+'</a><input type="checkbox" id="menu-item-chkbox-aed" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'AED'"+')"></input></div>'+
						'<div id="menu-item-aed" class="menu-item menu-item-lvl2">'+
							poiHtml['AED'] + 
						'</div>'+
					'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-canteen'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0007")+'</a><input type="checkbox" id="menu-item-chkbox-canteen" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'Canteen'"+')"></input></div>'+
						'<div id="menu-item-canteen" class="menu-item menu-item-lvl2">'+
							poiHtml['Canteen'] +
						'</div>'+
					'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-clinic'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0009")+'</a><input type="checkbox" id="menu-item-chkbox-clinic" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'Clinic'"+')"></input></div>'+
						'<div id="menu-item-clinic" class="menu-item menu-item-lvl2">'+
							poiHtml['Clinic'] +
						'</div>'+
					'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-lactationroom'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0025")+'</a><input type="checkbox" id="menu-item-chkbox-lactationroom" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'LactationRoom'"+')"></input></div>'+
						'<div id="menu-item-lactationroom" class="menu-item menu-item-lvl2">'+
							poiHtml['LactationRoom'] +
						'</div>'+
					'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-lecturetheatre'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0008")+'</a><input type="checkbox" id="menu-item-chkbox-lecutretheatre" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'LectureTheatre'"+')"></input></div>'+
						'<div id="menu-item-lecturetheatre" class="menu-item menu-item-lvl2">'+
							poiHtml['LectureTheatre'] +
						'</div>'+
					'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-prayerroom'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0026")+'</a><input type="checkbox" id="menu-item-chkbox-prayerroom" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'PrayerRoom'"+')"></input></div>'+
						'<div id="menu-item-prayerroom" class="menu-item menu-item-lvl2">'+
							poiHtml['PrayerRoom'] +
						'</div>'+
					'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-sportsfacility'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0018")+'</a><input type="checkbox" id="menu-item-chkbox-sportsfacility" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'SportsFacility'"+')"></input></div>'+
						'<div id="menu-item-sportsfacility" class="menu-item menu-item-lvl2">'+
							poiHtml['SportsFacility'] +
						'</div>'+
					'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-toilet'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0010")+'</a><input type="checkbox" id="menu-item-chkbox-toilet" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'Toilet'"+')"></input></div>'+
						'<div id="menu-item-toilet" class="menu-item menu-item-lvl2">'+
							poiHtml['Toilet'] + poiHtml['AccessibleToilet'] + 
						'</div>'+
					'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-waterstation'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0017")+'</a><input type="checkbox" id="menu-item-chkbox-waterstation" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'WaterStation'"+')"></input></div>'+
						'<div id="menu-item-waterstation" class="menu-item menu-item-lvl2">'+
							poiHtml['WaterStation'] + 
						'</div>'+
					poiHtml['Bank'] + 
					poiHtml['Bookstore'] + 
					poiHtml['CarPark'] + 
					poiHtml['Postbox'] + 
				'</div>'+
			'<div class="menu-item-div"><a onclick="gCampusMap._ToggleMenuItem(this,'+"'menu-item-publictransport'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span>'+getLabelByCurrLang("LBL0006")+'</a><input type="checkbox" id="menu-item-chkbox-publictransport" class="menu-item-chkbox" onclick="gCampusMap._ToggleMapMarker(this,'+"'PublicTransport'"+')"></input></div>'+
			'<div id="menu-item-publictransport" class="menu-item menu-item-lvl1">'+
				poiHtml['PublicTransport'] +
			'</div>'+
//			'<div class="menu-item-div">'+
//					'<a class="menu-item-poi" onclick="window.open('+"'"+'https://www.polyu.edu.hk/greenmap'+"'"+');"><span class="menu-icon glyphicon glyphicon-triangle-right"></span><span class="menu-item-poi-name">GreenMap@PolyU</span></a>' + 
//			'</div>'+
//			'<div id="menu-item-ack" class="menu-item-ack">'+ getLabelByCurrLang("LBL0015") +'</div>' +
		'</div>';
		mymap.controls[google.maps.ControlPosition.TOP_RIGHT].push(controlDiv);
	},
	_AddTilesToMap: function(mymap, mapBounds, pathPrefixOfTiles) {
		//TODO: refactor as batch mode
		var imageMapType = new google.maps.ImageMapType({
			getTileUrl: function(coord, zoom) {
				var proj = mymap.getProjection();
				var z2 = Math.pow(2, zoom);
				var tileXSize = 256 / z2;
				var tileYSize = 256 / z2;
				var tileBounds = new google.maps.LatLngBounds(
					proj.fromPointToLatLng(new google.maps.Point(coord.x * tileXSize, (coord.y + 1) * tileYSize)),
					proj.fromPointToLatLng(new google.maps.Point((coord.x + 1) * tileXSize, coord.y * tileYSize))
				);
				if (!mapBounds.intersects(tileBounds) || zoom < minimumZoomLevel || zoom > maximumZoomLevel) return null;
				return pathPrefixOfTiles+"/{z}/{x}/{y}.png".replace('{z}',zoom).replace('{x}',coord.x).replace('{y}',coord.y);
			},
			tileSize: new google.maps.Size(256, 256),
			minZoom: minimumZoomLevel,
			maxZoom: maximumZoomLevel,
			name: 'Tiles'			
		});		
		mymap.overlayMapTypes.push(imageMapType);		
	},	
};