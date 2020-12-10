// set the dates
var startDate = ee.Date.fromYMD(2019,2,6);
var endDate = ee.Date.fromYMD(2019,2,7);

//choose the location
// var luogo= Adamello;
// var luogo= Adamellopreciso;
// var luogo= AdamelloplusValle;
// var luogo= Generale;
var luogo= Tonale;
// var luogo= TonalePiste;
// var luogo= TonaleEst;
// var luogo= Presena;
// var luogo= Montagnevarie;

var S2= ee.ImageCollection('COPERNICUS/S2').filterDate(startDate,endDate);
S2=S2.max();
print(S2);

Map.addLayer(S2, {bands: ['B4', 'B3', 'B2'], min: 0, max: 10000}, 'RGB');

// Define a function to convert from degrees to radians.
function radians(img) {
  return img.toFloat().multiply(Math.PI).divide(180);
}

// Define a function to find the solar incidence angle
function solarlocalincidenceangle(az, ze, slope, aspect){
  var azimuth = radians(ee.Image(az));
  var zenith = radians(ee.Image(ze));
  return zenith.subtract(slope.multiply(azimuth.subtract(aspect).cos()));
}

// Define a function to find hillshade
function hillshade(az, ze, slope, aspect) {
  var azimuth = radians(ee.Image(az));
  var zenith = radians(ee.Image(ze));
  return azimuth.subtract(aspect).cos()
    .multiply(slope.sin())
    .multiply(zenith.sin())
    .add(
      zenith.cos().multiply(slope.cos())).max(ee.Image(0));
}

var hillfunction= function totale(S2){
  var dem = ee.Image("JAXA/ALOS/AW3D30_V1_1");
  var elevation = dem.select('AVE');
  var slope = ee.Terrain.slope(elevation);
  var aspect=ee.Terrain.aspect(elevation);
  var sza=  ee.Number(S2.get('MEAN_SOLAR_ZENITH_ANGLE'));
  var saz= ee.Number(S2.get('MEAN_SOLAR_AZIMUTH_ANGLE'));
  var shadows=ee.Terrain.hillShadow(elevation, saz, sza,10,true);
  var kernel = ee.Kernel.circle(15, 'meters');
  shadows = shadows
               .focal_min({kernel: kernel, iterations: 2})
               .focal_max({kernel: kernel, iterations: 2});
  var il=hillshade(saz, sza, radians(slope), radians(aspect));
  S2= S2.divide(il).multiply(shadows).updateMask(shadows.and(il.gt(0)));
  S2=S2.addBands(solarlocalincidenceangle(saz, sza, radians(slope), radians(aspect)).rename('SLIA'));
  S2=S2.addBands(elevation);
  return S2;
};

var copernicus = ee.ImageCollection('COPERNICUS/S2').filterDate(startDate,endDate).filterBounds(luogo).map(hillfunction);
print(copernicus);

var addBanda = function(image) {
  return image.addBands(image.normalizedDifference(['B2', 'B8']).rename('BandaNuova'));
};
var addNDSI = function(image) {
  return image.addBands(image.normalizedDifference(['B3', 'B11']).rename('NDSI'));
};
copernicus  = copernicus.map(addBanda);
copernicus  = copernicus.map(addNDSI);
//copernicus1=copernicus.addBands('SLIA');
var neveImage = ee.Image(copernicus.filterBounds(luogo).first());
Map.addLayer(copernicus, {bands: ['SLIA'], min: 0, max:2},'SLIA');
Map.addLayer(neveImage.visualize(['BandaNuova'], null, null, -0.1, 0.1,null,null ,['38AAFF','000000','FFAE32']));
Map.addLayer(neveImage.visualize(['NDSI'], null, null, -1, 1,null,null ,['800000','808000','0000FF','00FFFF']));

// sample N points from the 2-band image
var values = neveImage.sample({ region: luogo, scale: 20, factor:1, geometries: true}) ;
Map.addLayer(values.style({ color: 'red', pointSize: 1 }), {}, 'Samples');
//print("values",values)

// Creation of two layers:
// one on elevation (filtered on the area of interest)
// and another only for elevation above a predefined threshold.
var dem = ee.Image("JAXA/ALOS/AW3D30_V1_1");
var elevation = dem.select('AVE');
var clipelevation = elevation.clip(luogo);
//Map.addLayer(clipelevation, {min:0,max:1}, "AVE");
var elevationVis = {
  min: 0,
  max: 3000,
  palette: ['ffff00', 'ff0000','0000ff','00ffff', 'ffffff'],//yellow,red,blue,lightblue,white
};
// elevation layer
//Map.addLayer(clipelevation, elevationVis, 'Elevation'); se scommentato mostra l'elevazione dei punti
// anything below 2500 won't be shown
var HighMask = clipelevation.updateMask(clipelevation.gte(2500));
//Map.addLayer(HighMask,{palette:['ff00ff']}, 'HightMask');
print('HighMask',HighMask)
var chart = ui.Chart.feature.byFeature(values, 'SLIA', 'BandaNuova')
  .setChartType('ScatterChart')
  .setOptions({ pointSize: 2, pointColor: 'green', width: 100, height: 300, titleX: 'Angolo (Rad)', titleY: 'Diff Norm' })
//print(chart) ;

// Export the FeatureCollection.
Export.table.toDrive({
  collection: values,
  description: '06Febr2019TonaleNDSIfirst1',
  fileFormat: 'CSV'
});
Map.setCenter(10.612747377914616,46.255376611127154, 12);
