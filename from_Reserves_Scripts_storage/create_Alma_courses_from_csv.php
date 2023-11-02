<?php

$courses = fopen('/home/libmonitor/scripts/courses_for_alma.csv','r');

$ch_course = curl_init('https://api-na.hosted.exlibrisgroup.com/almaws/v1/courses');
$ch_instructor = curl_init();
curl_setopt($ch_course, CURLOPT_CUSTOMREQUEST, 'POST');
curl_setopt($ch_course, CURLOPT_HTTPHEADER, array('Content-Type: application/json','Authorization: apikey l7xxe54a24670acb4420afb92fc48c413472'));
curl_setopt($ch_instructor, CURLOPT_HTTPHEADER, array('accept: application/json','Authorization: apikey l7xx17674dc3a9af4dff85d3a78ef4ee2d8a'));
curl_setopt($ch_instructor, CURLOPT_RETURNTRANSFER, 1);

while(!feof($courses)) {
	$course = fgetcsv($courses);
	//If it's a blank line, ignore it
	if (empty($course[0])) {
		continue;
	}
	//If it's been cancelled, ignore it
	if ($course[1] == "Canceled") {
		continue;
	}
	//First, check to see if it's a lab. We're not loading labs.
	//JMB fixed 12/12/18; original version was missing the - in front of 5
	if (substr($course[2], 7, 1) == "L") {
		continue;
	}
	//We're not loading music lessons or ensembles, either
	if (substr($course[2],0,7) == "MUS-101" || substr($course[2],0,7) == "MUS-120" || substr($course[2],0,7) == "MUS-220" || substr($course[2],0,7) == "MUS-221") {
		continue;
	}
	//Or phys ed activities
	if (substr($course[2],0,7) == "PHE-100" || substr($course[2],0,7) == "PHE-101") {
		continue;
	}
	//Let's get the instructor first....
	$name = explode(',', $course[6]);
	$last_name = explode(' ',$name[0]);
	$first_name = explode(' ',$name[1]);
	//We need to drop middle initials/names, if they exist
	$instructor_q = "last_name~" . $last_name[0] . '%20AND%20first_name~' . $first_name[1];
	curl_setopt($ch_instructor, CURLOPT_URL, 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/users?q=' . $instructor_q);
	$alma_instructor = curl_exec($ch_instructor);
	$instructor = json_decode($alma_instructor);
	$alma_course['instructor'][]['primary_id'] = $instructor->user[0]->primary_id;
	//This assumes that the course name is formatted like it usually is, with the course ID and section in parentheses at the end. If it's not, you will get some curious codes.
	$alma_course['code'] = "FA-21-" . substr($course[2], 0, 7);
	$alma_course['section'] = substr($course[2], -2 ,2);
	var_dump($alma_course['section']);
	$alma_course['name'] = $course[3];
	$alma_course['academic_department']['value'] = substr($course[2], 0, 3);
	$alma_course['processing_department']['value'] = "001"; 
	$alma_course['start_date'] = "2021-08-01Z";
	$alma_course['end_date'] = "2021-12-18Z";
	//The only valid terms are "AUTUMN" and "SPRING." "FALL" is NOT a valid term.
	$alma_course['term'][]['value'] = "AUTUMN";
	$alma_course['status'] = "INACTIVE";
	$alma_course['searchable_id'] = [substr($course[2], 0, 7), $course[3], $course[0]];
	curl_setopt($ch_course, CURLOPT_POSTFIELDS, json_encode($alma_course));
	$result = curl_exec($ch_course);
	var_dump($result);
	$alma_course['term'] = [];
	$alma_course['instructor'] = [];
}

?>
