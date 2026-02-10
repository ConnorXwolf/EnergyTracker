# 🔋 EnergyTracker

## 🌟 The Story Behind the Project

**EnergyTracker** was born out of a personal battle.

As a developer living with **Fibromyalgia** and other chronic illnesses, I realized that traditional "productivity" apps are often discouraging. They focus on how much you can *do*, rather than how much you can *sustain*. In the chronic illness community, we often refer to "Spoon Theory"—the idea that we have a limited amount of energy (spoons) each day.

I built this app to help myself—and others with similar special needs—visualize their daily "HP" (Health Points). It is a tool designed to help you practice **Pacing**, avoid "crash and burn" cycles, and communicate your energy patterns with health professionals.

---

## ✨ What is EnergyTracker?

EnergyTracker is a desktop companion that treats your energy like a rechargeable battery.

* **Tasks** (Chores, Work, Socializing) consume your HP.
* **Exercises & Rest** (Physical Therapy, Naps, Light Stretching) restore your HP.
* **The Goal** is to stay balanced and avoid hitting 0%.

---

This is the complete, high-fidelity **README.md** for your project. I have structured it to be accessible, supportive, and clear, specifically highlighting the "Game-like" HP logic and the accessibility settings for users with chronic conditions.

---

# 🔋 EnergyTracker

### *A Personal Pacing Tool Built by a Developer with Fibromyalgia*

## 🌟 The Story Behind the Project

**EnergyTracker** was born from necessity. Living with **Fibromyalgia** and chronic illness means that "productivity" isn't just about getting things done—it's about managing a very limited supply of energy.

This app is designed to help you practice **Pacing**. By treating your physical and mental energy like a video game "HP" (Health Points) system, you can visualize your capacity, avoid the "crash and burn" cycle, and keep a reliable record of your wellbeing for yourself and your doctors.

---

## 🎮 The HP System: Your Daily Stats

The app uses three core metrics to determine your daily capacity. While the main screen shows a simplified ring, you can click **"More"** to see the full breakdown:

| Color | Element | Game Analogy | Meaning |
| --- | --- | --- | --- |
| 🟡 **Yellow** | **Stamina** | Physical Energy | Your body's physical capacity (movement, chores). |
| 🔵 **Blue** | **Mana** | Mental Energy | Your mood, cognitive load, and "brain" levels. |
| 🔴 **Red** | **Fatigue** | Damage Taken | Your sleepiness level and the "drain" from lack of rest. |

### 📈 The Calculation

Your functional energy is calculated using this formula:
$$HP = (\text{Stamina} + \text{Mana}) - \text{Fatigue}$$

---

## 📖 User Guide

### 1. Calendar and Events

The Calendar is your command center for the month.

* **Navigate**: Click any date to view what you achieved or planned for that specific day.
* **Highlights**: Dates with recorded tasks or health events are highlighted so you can quickly see your "busy" days.
* **Unified List**: Below the calendar, you will see a combined list of both your appointments (Events) and your To-Dos (Tasks) for a clear view of your day's "cost."

### 2. Daily Exercise 

* **Track Progress**: Use the Exercise Manager to log cardio exercise, stretching, or muscle building.
* **Visual Feedback**: Progress bars show how close you are to your daily goal.


### 3. Tasks (Energy Consumption)

Manage your daily chores and work with **Priority Levels**.

* **Add Tasks**: Group tasks by category (e.g., Work, Home, Medical).
* **Prioritize**: Assign "Low," "Medium," or "High" priority. 


### 4. Monthly HP Tracker (The "More" Button)

Click the **"More"** button to enter the deep-dive analysis.

* **31-Day Ring**: View your entire month as a circular visualization.
* **Color-Coded Health**: Each day's segment is colored based on your total HP. 🔴 indicate "Crash Days," while 🟢show when you successfully stayed within your limits.
* **Trend Analysis**: Hover over segments to see exactly why a day was difficult (e.g., was it high Fatigue or low Mana?).

### 5. Accessibility & UI Settings

Chronic illness often comes with visual fatigue or "brain fog." You can customize the app to be easier on your eyes:

* **UI Scaling**: Go to **Settings** to increase the overall scale of the interface (e.g., 1.2x or 1.5x) to make buttons easier to hit.
* **Text Size**: Independently adjust the font size to ensure all instructions and labels are clear and readable without strain.

### 🔒 Privacy & Safety

* **100% Offline**: Your health data is yours alone. It is stored in a file named `energy_tracker.db` on your computer. Nothing is ever uploaded to the internet.
* **No Medical Advice**: This app is a tracking tool, not a doctor. Always listen to your body over the app’s numbers.

---

## 🚀 How to Install

### Option A: The Easy Way (Windows)

1. Download the `EnergyTracker.zip` from the latest release.
2. Extract the folder and double-click **EnergyTracker.exe**.
3. No installation process is required!

### Option B: For Python Users

1. Download the source code.
2. Install the requirements:
```bash
pip install -r requirements.txt

```


3. Run the application:
```bash
python main.py

```


---

## 💬 A Note from the Developer

I am developing this app as my energy allows. If you have suggestions on how to make the interface easier to use for people with brain fog, visual impairments, or chronic pain, please open an **Issue** or reach out.

**Gentle reminder: You are more than your productivity.**

---

*Created with care for the chronic illness community.*
