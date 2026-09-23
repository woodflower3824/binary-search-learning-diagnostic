from flask import Flask, render_template, request
import json

app = Flask(__name__)

def load_questions():
	with open("questions.json", "r", encoding="utf-8") as f:
		return json.load(f)
							
def evaluate_answer(answer, key_concepts):
	answer = answer.replace(" ","").lower()
	
	score = 0
	missing_concepts = []

	for concept in key_concepts:
	
		found = False
		negative_found = False
	
		for words in concept["negative_keywords"]:
			if all(keyword in answer for keyword in words):
				negative_found = True
				break
			
		if not negative_found:		
			for group in concept["keywords"]:
				normalized_group = [keyword.replace(" ", "").lower() for keyword in group]
				
				if all (keyword in answer for keyword in normalized_group):
					found = True
					break
					
		if found and not negative_found:			
			score += 1
		else:
			missing_concepts.append(concept["concept"])
		
	return score, missing_concepts

#使用者進入網頁/時,執行home()
@app.route("/", methods = ["GET", "POST"])
def home():
	
	questions = load_questions() 
	
	if request.method == "POST":
		
		index = int(request.form["index"])
		answer = request.form["answer"]
		
		question = questions[index]
		
		score, missing_concepts = evaluate_answer(answer, question["key_concepts"])			
		
		percentage = score / len(question["key_concepts"]) * 100		
																											
		return render_template(
			"index.html",
			question = question,
			index = index,
			total = len(questions),
			submitted = True,
			answer = answer,
			percentage = percentage,
			missing_concepts = missing_concepts
		) 
	return render_template(
			"index.html",
			question = questions[0],
			index = 0,
			total = len(questions),
			submitted = False
		) 

@app.route("/question/<int:index>")
def show_question(index):
	
	questions = load_questions()	
	question = questions[index]
		
	#如果是 Trace 小題,找出同一組 Trace 的原題 
	trace_question = None
		
	if question["type"] == "Trace" and "step" in question:
			
		for q in questions:
				
			if(
				q["type"] == "Trace"
				and q.get("trace_id") == question.get("trace_id") #確認題目是Trace小題
				and "step" not in q #找到沒有step的原題
			):
				trace_question = q
				break
		
	return render_template(
		"index.html",
		question = question,
		index = index,
		total = len(questions),
		submitted = False,
		trace_question = trace_question
	) 
	
@app.route("/interactive/<int:index>", methods=["GET", "POST"])
def interactive(index):
	questions = load_questions()
	question = questions[index]
	
	arr = question["array"]
	target = question["target"]
	
	found = False
	correct_direction = None
	
	# 第一次進入題目
	if request.method == "GET":
		left = 0
		right = len(arr) - 1
		count = 1
		feedback = None
				
	# 使用者按下按鈕
	else:
		left = int(request.form["left"])
		right = int(request.form["right"])
		count = int(request.form["count"])	
		
		mid = (left + right) // 2
		choice = request.form["choice"]
		
		#使用者確認已找到 target
		if choice == "found":
			found = True
			feedback = "✓ 找到target"	
	
		else:
			
			# 判斷正確搜尋方向
			if target > arr[mid]:
				correct_choice = "right"
			else:
				correct_choice = "left"
			
			if correct_choice == "right":
				correct_direction = "往右"	
			
			else:
				correct_direction = "往左"	
			
			# 分析使用者選擇		
			if choice == correct_choice:
				feedback = "✓ 判斷正確"
			
			else:
				feedback = "✗ 判斷錯誤"	
		
			#不論答案是否正確,都按照正確方向更新
			if correct_choice == "right":
				left = mid + 1
			else:
				right = mid - 1
													
			count += 1	
			
	#根據目前搜尋範圍重新計算 mid
	mid = (left + right) // 2
	
	return render_template(
		"interactive.html",
		question = question,
		index = index,
		arr = arr,
		target = target,
		left = left,
		right = right,
		mid = mid,
		count = count,
		found = found,
		feedback = feedback,
		correct_direction = correct_direction
		)		
									
if __name__ == "__main__":
	app.run(host= "0.0.0.0", port=5002, debug=False)  	
	
