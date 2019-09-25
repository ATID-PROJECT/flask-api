from dynaconf import settings
import requests
import sys

def getQuiz( url_base, token, course_id, quiz_id ):
    function = "get_quiz"

    params = f"&quiz_id={quiz_id}&course_id={course_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))

    r = requests.post( final_url, data={} )
    result = r.json()

    return result

def createQuiz(url_base, token, course_id, name, description, group_id):
    
    function = "local_wstemplate_handle_quiz"
    params = f"&course_id={course_id}&name={name}&description={description}&group_id={group_id}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    print(final_url, file=sys.stderr)
    print("..............", file=sys.stderr)
    r = requests.post( final_url, data={} )

    result = r.json()

    return result

def updateQuiz(url_base, token, quiz_id, name, description):
    
    function = "update_quiz"
    params = f"&quiz_id={quiz_id}&name={name}&description={description}"
    final_url = str( url_base + "/" +(settings.URL_MOODLE.format(token, function+params)))
    
    r = requests.post( final_url, data={} )
    result = r.json()

    return result