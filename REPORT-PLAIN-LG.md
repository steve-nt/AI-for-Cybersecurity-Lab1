# Lab 1: Building Your First Intrusion Detector
## The same results, explained in plain language

**Dataset:** CICIDS2017, all eight day-files combined
**Random seed:** 42 · **Code:** `src/` + `run_all.py` · **Results:** `results-all-cvs/`
**Authors:** [NAME A] and [NAME B]

> This is a plain-English companion to `REPORT-ALL=CVS.md`. Same run, same numbers, no jargon left
> unexplained. If you want the formal version, read that one instead.

---

## 1. What we built

A program that looks at a record of a network connection and decides: **is this normal, or is
somebody attacking us?**

The old way to do this is to write rules by hand - *"if one computer opens more than 500 connections
in a minute, sound the alarm"*. That works until an attacker does something the rule-writer did not
think of.

Instead we showed a computer program about 268,000 examples of real connections, each labelled
"normal" or with the name of an attack, and let it work out the difference by itself.

We built it twice:

- **Version 1 - the alarm.** Normal or attack? A yes/no answer.
- **Version 2 - the diagnosis.** *Which* attack is it? A port scan, a flood, a password-guessing
  attempt, and so on.

You need both. The alarm tells you something is wrong. The diagnosis tells you what to do about it,
because you do not respond to a traffic flood the way you respond to someone injecting SQL into your
login form.

## 2. The data

We used CICIDS2017: a real network that researchers built in 2017, ran normal office activity on for
a week, and attacked on a schedule while recording everything. Each row is one connection described
by about 78 measurements - how long it lasted, how many bytes went each way, how big the packets
were.

We combined **all eight days**: **2,830,743 connections** in total.

Here is the first important fact:

| | Share |
|---|---|
| Normal traffic (BENIGN) | **80.3%** |
| Everything else - 14 kinds of attack | 19.7% |

**Four out of every five connections are perfectly innocent.** Hold on to that number, because it is
about to matter enormously.

The attacks are also wildly uneven. `DoS Hulk` appears 231,073 times. `Heartbleed` appears **11
times** in nearly three million rows.

## 3. Cleaning the data, and why each step matters

Raw data cannot be fed to a model as-is. Four things had to go.

**Name tags.** Some columns identify *who* and *when* - IP addresses, timestamps, port numbers. If
you leave those in, the model does not learn what an attack looks like. It learns "traffic from
192.168.10.50 is bad". That scores brilliantly on your test, and it is worthless in real life,
because tomorrow the attacker uses a different address. This mistake has a name: **data leakage**.

> **Honest note:** the version of the dataset we downloaded had already had most of these removed by
> the people who published it. We only had two left to drop. We are not taking credit for removing
> things that were never there.

**Broken numbers.** Some columns are "bytes divided by how long the connection lasted". When the
connection lasted zero time, the answer is infinity. No model can do arithmetic with infinity, so
those rows had to go.

**Duplicates.** Over a hundred thousand rows appeared more than once. This is more dangerous than it
sounds: the same row can end up in the practice set *and* the exam set, so the model gets tested on
something it has already memorised. Your score comes out looking great and means nothing.

**Dead columns.** Some columns have the same value in every single row. They cannot help you tell
anything apart, so we dropped them.

**One special case.** Three attacks are almost nonexistent - Heartbleed has 11 examples, SQL
Injection 21, Infiltration 36. We used a fifth of the data to keep things fast, but a fifth of 11 is
2, and 2 examples cannot be split into practice, tuning and exam sets. Those classes would sit in
the practice set and never appear in the exam - present but never actually graded. So we kept the
tiny classes whole instead of sampling them.

**After all that: 446,645 connections with 68 measurements each.**

## 4. How we tested honestly

This part is worth more marks than anything else, so it is worth explaining carefully.

We split the data into three piles:

| Pile | Size | What it is for |
|---|---|---|
| **Training** (60%) | 267,987 | The model learns from this. It sees the answers. |
| **Validation** (20%) | 89,329 | We try different settings and pick the best using this. |
| **Test** (20%) | 89,329 | Locked in a drawer. Opened once, at the very end. |

Think of it as revision, mock exam, and real exam.

**Why the third pile exists.** We want to know how the detector will do on traffic it has genuinely
never seen. The moment you use the test set to make a decision - try a setting, peek, try another -
it is not unseen any more, and your final number becomes a lie you told yourself. So we chose every
setting on the validation pile and touched the test pile exactly once per model.

**Splitting fairly.** We made sure each of the 15 attack types appears in the same proportion in all
three piles. Otherwise a rare attack could land entirely in one pile by chance - so the model never
learns it, then gets examined on it.

**One subtle trap we avoided.** We rescaled the measurements onto a common range (explained in
section 7), and we worked out how to rescale using **only the training pile**. If we had used all the
data to decide that, information about the exam would have leaked backwards into revision.

## 5. The models we tried

| Model | How it works |
|---|---|
| **Logistic Regression** | Draws one straight dividing line between normal and attack. Simplest possible approach. |
| **Random Forest** | Builds 300 flowcharts of yes/no questions, each on a random slice of the data, then lets them vote. |
| **Neural network (MLP)** | Layers of simple units; each learns a small piece of the pattern, later layers combine earlier ones. |

For each we tried two or three settings and kept whichever did best **on the validation pile**.

## 6. The results, and what they actually mean

The exam was **89,329 connections: 75,868 normal and 13,461 attacks.**

Five numbers get reported. Here is what each one is really asking:

| Number | The plain-English question | Which way is good |
|---|---|---|
| **Accuracy** | Of everything, how much did it get right? | higher |
| **Recall** | Of the real attacks, how many did it catch? | higher |
| **FAR** (false alarm rate) | Of the innocent traffic, how much did it wrongly accuse? | **lower** |
| **macro-F1** | Is it good at *both* jobs, not just the easy one? | higher |
| **ROC-AUC** | Shown one attack and one normal, does it find the attack more suspicious? | higher |

**The scores:**

| Model | Accuracy | macro-F1 | Recall | ROC-AUC | FAR |
|---|---|---|---|---|---|
| Logistic Regression | 0.9721 | 0.9419 | 0.8330 | 0.9915 | 0.0032 |
| **Random Forest** | **0.9984** | **0.9968** | **0.9923** | **0.9999** | **0.0006** |
| Neural network (MLP) | 0.9949 | 0.9901 | 0.9814 | 0.9994 | 0.0027 |

Percentages are hard to feel. Here are the same results as **counts of actual connections**:

| Model | Attacks caught | **Attacks missed** | False alarms |
|---|---|---|---|
| Logistic Regression | 11,213 | **2,248** | 245 |
| **Random Forest** | **13,357** | **104** | **42** |
| Neural network (MLP) | 13,210 | 251 | 202 |

### The one thing to take away from this report

Look at Logistic Regression. **97.2% accuracy.** That sounds like a good detector. Most people would
be pleased with it.

It missed **2,248 attacks. More than one in six walked straight past it.**

Random Forest missed 104.

Those two models are 2.6 percentage points apart on accuracy. They are **22 times apart** on attacks
let through. Accuracy hid that difference completely.

### Why accuracy lies here

Remember that 80.3% of connections are normal. Imagine a program that does not look at its input at
all and simply answers "normal" every single time.

**It scores 80.3% accuracy. It catches zero attacks.** It is completely worthless, and on paper it
looks like a respectable B.

That is why the lab bans arguing from accuracy alone, and why **macro-F1** is our headline number
instead. macro-F1 scores the "normal" job and the "attack" job separately and then averages them,
giving each equal weight. The lazy always-say-normal program scores brilliantly on one and zero on
the other, so its average collapses and the fraud is exposed immediately.

### Why the false alarm rate is not enough either

Here is the subtlety that makes this run interesting.

Logistic Regression's false alarm rate (0.0032) is **low** - it looks well-behaved. But part of the
reason it rarely cries wolf is that it rarely says "attack" at all. On data that is 80% innocent,
staying quiet is an easy way to look calm while intruders walk in.

**So FAR and recall have to be read together.** A model can cheat either one on its own. macro-F1 is
the number that catches both kinds of cheating at once.

## 7. The experiment: does rescaling matter?

An experiment where you **change exactly one thing** and keep everything else identical is called an
ablation. Ours: give the model rescaled measurements, or raw ones.

**Why rescaling might matter.** One column is "how long the connection lasted", measured in
millionths of a second, running into the millions. Another counts flags, and runs from 0 to 8. To a
model that adds up weighted numbers, the first column looks hugely more important purely because its
numbers are bigger. Rescaling puts everything on a comparable footing and removes that unfair
advantage.

| Model | macro-F1 raw → rescaled |
|---|---|
| Logistic Regression | 0.9033 → **0.9419** |
| Neural network (MLP) | 0.9425 → **0.9901** |
| Random Forest | 0.9968 → 0.9968 |

The first two improve clearly. **Random Forest does not budge.**

That is not luck, it is how the models work. Random Forest asks questions like *"is this value above
500?"*, and that question means exactly the same thing whether you measure in seconds or
microseconds. It is blind to scale by design. The other two add up weighted numbers, so scale is
everything to them.

**A bonus piece of evidence.** When we trained Logistic Regression on raw numbers, the software
printed a warning: it had tried 1,000 rounds of adjustment and still not settled on an answer. On
rescaled numbers the same model settled after **170 rounds**. We can watch the difficulty directly,
not just infer it from the scores.

## 8. Naming the attack

Now the harder job: not "is this an attack" but "*which* attack". The number below is the share of
that attack the model correctly identified.

**Caught almost perfectly:**

| Attack | Caught |
|---|---|
| Normal traffic | 100% |
| DDoS | 100% |
| FTP password guessing | 100% |
| Heartbleed | 100% |
| DoS Hulk | 99% |
| DoS GoldenEye, DoS slowloris | 98% |
| DoS Slowhttptest | 97% |

These are floods and password-guessing attacks. They are **loud**. Hammering a server looks nothing
like reading email, so they are easy to spot.

**Caught most of the time:**

| Attack | Caught |
|---|---|
| SSH password guessing | 93% |
| Port scanning | 91% |

**Struggled:**

| Attack | Caught | What went wrong |
|---|---|---|
| Web brute force | 75% | Confused with XSS |
| Botnet | 65% | A third labelled as normal traffic |
| Web XSS | 35% | Mostly confused with web brute force |

The web attacks get mistaken **for each other**. Both are attacks delivered over ordinary web
traffic, and at the level of "how big were the packets, how long did it take" they look nearly
identical. Telling them apart would need reading the actual contents of the messages, which this
dataset does not include. That is a limit of the *information available*, not of the model.

The botnet result makes sense too. A botnet's whole design goal is to look like normal traffic while
it talks to its controller. It is supposed to be hard.

**Completely missed:**

| Attack | Caught |
|---|---|
| Infiltration | **0%** |
| SQL Injection | **0%** |

Every single example of both was labelled "normal traffic". These are the two rarest attacks in the
data - 36 and 21 examples out of nearly three million. The model saw almost none during training and
effectively learned to ignore them.

**We are reporting this rather than hiding it, and it is the most valuable finding here.** The yes/no
detector looked nearly flawless, because these attacks are a rounding error among 13,461. Only by
asking the model to *name* the attack did we discover that two attack types are completely invisible
to it. A detector with a blind spot you know about is far better than one with a blind spot you do
not.

## 9. What we would actually deploy, and why

**Random Forest.** It is the best on every measure at once - it catches the most attacks *and* raises
the fewest false alarms. There is no trade-off to weigh up.

**Why false alarms decide this.** Picture a company network carrying a million normal connections a
day:

| Model | False alarms per day |
|---|---|
| **Random Forest** | **~554** |
| Neural network | ~2,663 |
| Logistic Regression | ~3,229 |

554 alerts a day is a real workload, but a small team can get through it.

3,229 is **one every 27 seconds, all day and all night**. Nobody reads that. Within a fortnight the
alerts are muted or the system is switched off - and now you are worse off than having no detector,
because everyone believes the network is being watched when it is not.

That is the whole reason false alarm rate belongs in the table next to accuracy. Two models a couple
of accuracy points apart can be a working security tool and an ignored nuisance.

## 10. What this system cannot do

Being straight about limits is part of the job.

- **Two attacks are completely invisible to it** - Infiltration and SQL injection. It would never
  warn you about either.
- **The rarest attacks rest on a handful of examples.** Heartbleed scored 100%, but on so few test
  cases that the number proves nothing.
- **This was a laboratory network.** Researchers built it, scripted the attacks and ran them on a
  timetable. Real traffic is messier and real attackers are less predictable.
- **We used a fifth of the data**, to keep training to minutes rather than hours.
- **We only see traffic shapes, never contents.** That is why two web attacks are inseparable here.
- **The scores are suspiciously high, and we should say so.** Nearly 18% of this data is high-volume
  floods that look nothing like normal browsing. That makes the yes/no job genuinely easy. We are
  confident there is no cheating - the exam set was sealed before training, opened once, and
  duplicates were removed first - but an easy exam produces high marks.
- **This is 2017 traffic.** Attacks from eight years ago may not resemble what is used today.

## 11. Who did what

> **[FILL IN BEFORE SUBMITTING.]**
>
> [NAME A] handled the data side - loading, cleaning, splitting. [NAME B] handled the models and the
> scoring. [NAME A] wrote sections 1-5, [NAME B] wrote sections 6-10. Both of us ran the whole thing
> end to end and got matching numbers.

## 12. Did we use AI?

Yes, and we are saying so plainly because the lab requires it.

We used Claude (an AI assistant made by Anthropic) to help set up the project structure, draft the
code, work out why one rare attack class was disappearing from our test set, and draft this report.

We read and ran all the code ourselves. **Every number in this document came out of our own program
running on our own data** - none of it was supplied by the assistant. We understand what the code
does and can explain any part of it.

## 13. Running it yourself

| | |
|---|---|
| Random seed | 42, in `src/config.py` |
| Language | Python 3.11 |
| Libraries | scikit-learn, pandas, numpy, matplotlib, joblib, tabulate |
| Command | `python run_all.py` |

The seed is a fixed number that makes the random choices repeatable, so running it again gives
exactly the same answers.
