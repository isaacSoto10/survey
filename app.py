from flask import Flask, request, render_template, redirect, flash, session
from flask_debugtoolbar import DebugToolbarExtension
from surveys import surveys

# key names will use to store some things in the session;
# put here as constants so we're guaranteed to be consistent in
# our spelling of these
RESPONSES_KEY = "responses"
current_survey_key = "current_survey"


app = Flask(__name__)
app.config['SECRET_KEY'] = "never-tell!"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

debug = DebugToolbarExtension(app)


@app.route("/")
def show_a_survey():
    '''show_a_survey'''
    return render_template ('start.html', survey=survey)


@app.route("/begin", methods=["POST"])
def start_survey():
    """Clear the session of responses."""

    session[RESPONSES_KEY] = []

    return redirect("/questions/0")






@app.route("/answer", methods=["POST"])
def handle_question():
    choice = request.form["answer"]
    text = request.form.get("text", "")
    responses = session[RESPONSES_KEY]
    responses.append({"choice":choice, "text":text})
    session[RESPONSES_KEY] = responses
    responses = session[RESPONSES_KEY]
    survey_code = session[current_survey_key]
    survey = surveys[survey_code]


    if(len(responses)== len(survey.questions)):
        return redirect('/complete')
    else:
        return redirect (f"/questions/{len(responses)}")




















@app.route("/questions/<int:qid>")
def show_question(qid):
    """Display current question."""
    responses = session.get(RESPONSES_KEY)
    survey_code = session[current_survey_key]
    survey = surveys[survey_code]

    if (responses is None):
        # trying to access question page too soon
        return redirect("/")

    if (len(responses) == len(survey.questions)):
        # They've answered all the questions! Thank them.
        return redirect("/complete")

    if (len(responses) != qid):
        # Trying to access questions out of order.
        flash(f"Invalid question id: {qid}.")
        return redirect(f"/questions/{len(responses)}")

    question = survey.questions[qid]
    return render_template(
        "questions.html", question_num=qid, question=question)

















@app.route("/complete")
def complete():
    """Survey complete. Show completion page."""
    survey_id = session[current_survey_key]
    survey = surveys[survey_id]
    responses = session[RESPONSES_KEY]

    html= render_template("completion.html", survey=survey, responses=responses)

    response = make_response(html)
    response.set_cookie(f"completed_{survey_id}", "yes", max_age=60)
    return response


