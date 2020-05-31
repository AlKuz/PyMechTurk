"""The example from the MTurk documentation"""

from pymechturk.qualification import xml_generator as gen


overview = gen.Content() \
    .add_title("Game 01523, 'X' to play") \
    .add_text("You are helping to decide the next move in a game of Tic-Tac-Toe. The board looks like this:") \
    .add_image(url="http://tictactoe.amazon.com/game/01523/board.gif",
               alt_text="The game board, with 'X' to move.") \
    .add_text("Player 'X' has the next move.")

question_1 = gen.Question(
    question_id="nextmove",
    name="The Next Move",
    is_required=True,
    content=gen.Content().add_text("What are the coordinates of the best move for player 'X' in this game?"),
    answer=gen.FreeTextAnswer(
        min_length=2,
        max_length=2,
        default_text="C1"))

question_2 = gen.Question(
    question_id="likelytowin",
    name="The Next Move",
    is_required=True,
    content=gen.Content().add_text("How likely is it that player 'X' will win this game?"),
    answer=gen.SelectionAnswer(
        answer_style="radiobutton",
        selections={
            "notlikely": "Not likely",
            "unsure": "It could go either way",
            "likely": "Likely"}))

question_form = gen.QuestionForm() \
    .add_overview(overview) \
    .add_question(question_1) \
    .add_question(question_2)

answer_key = gen.AnswerKey() \
    .add_question_keys(question=question_1,
                       keys={5: ["D"]}) \
    .add_question_keys(question=question_2,
                       keys={10: ["apples"]}) \
    .add_max_score(15)

print(question_form.to_string())
print(answer_key.to_string())
