<?php

$semester = "Fall 2021";

$courses = file_get_contents("/home/libmonitor/scripts/courses500.json");
$courses = json_decode($courses);

$ares_course_file = fopen('/home/libmonitor/scripts/courses.txt','a+');
$ares_course_user_file = fopen('/home/libmonitor/scripts/courseusers.txt','a+');
#https://stackoverflow.com/questions/26805959/fputcsv-with-tab-delimiter
#fwrite($ares_course_file, "sep=\t".PHP_EOL);
#fwrite($ares_course_user_file, "sep=\t".PHP_EOL);

$ch_almacourse = curl_init();
#curl_setopt($ch_almacourse, CURLOPT_HTTPHEADER, array('accept: application/json','Authorization: apikey l7xx17674dc3a9af4dff85d3a78ef4ee2d8a'));
curl_setopt($ch_almacourse, CURLOPT_HTTPHEADER, array('accept: application/json','Authorization: apikey l7xxe54a24670acb4420afb92fc48c413472'));
curl_setopt($ch_almacourse, CURLOPT_RETURNTRANSFER, 1);

foreach($courses->results as $course) {
	//Let's get the course from Alma first. If it's not in Alma (if we filtered it out because it was a lab or a phys ed activity) we're not loading it into Ares, either.
	$course_q = "searchable_ids~" . $course->externalId;
	curl_setopt($ch_almacourse, CURLOPT_URL, 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/courses?q=' . $course_q);
	echo $course_q . "\n";
	$alma_course = curl_exec($ch_almacourse);
	$alma_course = json_decode($alma_course);
	if($alma_course->total_record_count == 0) {
		echo "Course not found";
		continue;
	}

	$ares_course['RegistrarCourseID'] = $course->externalId;
	$ares_course['ExternalCourseID'] = $course->uuid;
	$ares_course['Name'] = $course->name;
	$ares_course['Semester'] = $semester;
	$ares_course['CourseNumber'] = substr($course->name,-11,10);
	$ares_course['DefaultPickupSite'] = "MAIN";
	//fputcsv($ares_course_file, $ares_course, "\t");
	//Can't do this because it wraps things in quotes, which messes up Ares
	//Using this instead: https://stackoverflow.com/questions/1800675/write-csv-to-file-without-enclosures-in-php
	fputs($ares_course_file, implode($ares_course, "\t")."\n");

	if ($alma_course->course[0]->instructor) {
		$instructor_pcard = $alma_course->course[0]->instructor[0]->primary_id;
		curl_setopt($ch_almacourse, CURLOPT_URL, 'https://api-na.hosted.exlibrisgroup.com/almaws/v1/users/' . $instructor_pcard);
		$instructor_almarecord = curl_exec($ch_almacourse);
		$instructor_almarecord = json_decode($instructor_almarecord);
		$ares_course_user['RegistrarCourseID'] = $course->externalId;
		$instructor_email = explode('@',$instructor_almarecord->contact_info->email[0]->email_address);
		$ares_course_user['LibraryID'] = $instructor_email[0];
		$ares_course_user['UserType'] = "Instructor";
		fputcsv($ares_course_user_file, $ares_course_user, "\t");
	}
}

fclose($courses);
fclose($ares_course_file);
fclose($ares_course_user_file);

?>
