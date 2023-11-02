<?php

$ch_courselist = curl_init();
$ch_course = curl_init();
curl_setopt($ch_course, CURLOPT_CUSTOMREQUEST, 'PUT');
curl_setopt($ch_course, CURLOPT_HTTPHEADER, array('Content-Type: application/json','Authorization: apikey l7xxe54a24670acb4420afb92fc48c413472'));
curl_setopt($ch_courselist, CURLOPT_HTTPHEADER, array('Content-Type: application/json','Authorization: apikey l7xxe54a24670acb4420afb92fc48c413472'));

$url = 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/courses';
$url .= '?' . urlencode('limit') . '=' . urlencode('100') . '&' . urlencode('offset') . '=' . urlencode('0') . '&' . urlencode('order_by') . '=' . urlencode('start_date') . '&' . urlencode('direction') . '=' . urlencode('DESC') . '&' . urlencode('apikey') . '=' . urlencode('l7xxe54a24670acb4420afb92fc48c413472') . '&' . urlencode('format') . '=' . urlencode('json');
$response = file_get_contents($url);
$courses = json_decode($response);
//var_dump($courses);
foreach($courses->course as $course) {
	//update the start date
	if ($course->start_date == "2021-01-25Z") {
	  $courseurl = "https://api-na.hosted.exlibrisgroup.com/almaws/v1/courses/" . $course->id;
//	  echo $courseurl;
	  $alma_course['code'] = "SP1-21-" . substr($course->code, 7,7);
	  echo $alma_course['code'];
//	  $alma_course['start_date'] = "2019-08-23Z";
//	  $alma_course['status'] =  "ACTIVE";
	  curl_setopt($ch_course, CURLOPT_POSTFIELDS, json_encode($alma_course));
	  curl_setopt($ch_course, CURLOPT_URL, $courseurl);
  	  $result = curl_exec($ch_course);
          var_dump($result);	
	}
}


?>
