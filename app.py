from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)


class Expense(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    amount = db.Column(db.Float, nullable=False)

@app.route("/")
def home():
    
    expenses = Expense.query.all()
    
    total = sum(expense.amount for expense in expenses)
    entry_count = len(expenses)
    category_totals = {}

    for expense in expenses:
        if expense.category in category_totals:
            category_totals[expense.category] += expense.amount
        else:
            category_totals[expense.category] = expense.amount

    labels = list(category_totals.keys())
    values = list(category_totals.values())

    insights = []

    if entry_count == 0:
        insights.append("No expenses recorded yet.")
    else:

        highest_category = max(
            category_totals,
            key=category_totals.get
        )

        highest_amount = category_totals[highest_category]

        percentage = (highest_amount / total) * 100

        insights.append(
            f"Highest spending category: {highest_category}"
        )

        insights.append(
            f"Total spending: ₹{total:.2f}"
        )

        insights.append(
            f"You have logged {entry_count} expenses."
        )

        insights.append(
            f"{highest_category} accounts for {percentage:.1f}% of your spending."
        )

        if percentage > 50:
            insights.append(
                "Consider reducing discretionary spending."
            )
        else:
            insights.append(
                "Your spending appears reasonably balanced."
            )

    return render_template(
    "index.html",
    expenses=expenses,
    total=total,
    entry_count=entry_count,
    labels=labels,
    values=values,
    insights=insights
)

@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    category = request.form["category"]
    amount = request.form["amount"]

    new_expense = Expense(
    title=title,
    category=category,
    amount=float(amount)
)

    db.session.add(new_expense)
    db.session.commit()

    return redirect("/")


@app.route("/delete/<int:id>")
def delete(id):
    expense = Expense.query.get_or_404(id)

    db.session.delete(expense)
    db.session.commit()

    return redirect("/")

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)
