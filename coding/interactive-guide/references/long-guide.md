# Long-guide workflow

Use this for a guide of six or more pages, or one the user calls long. The stops cost time, so skip them for anything shorter.

## 1. Plan

Write `plan.md` beside the guide. It is the memory of the run; reread it rather than trusting the conversation.

- The reader, and what they can do at the end.
- The page list: id, title, the one question it answers, its blocks, and which figures and quizzes it needs.
- The sources for each page, and any gaps.

Check it yourself before moving on. Each page should assume only earlier pages, each figure should serve a named point, and blocks should follow the content, not fill it out. Then send the plan to the user with the open decisions listed one by one, each with your recommendation, and wait. A single "all fine?" hides choices from them.

## 2. First spread

Create the guide directory and write only the cover data and the first page. List that one page in `guide.json` and build. With one page the tabs are hidden, which is expected at this stage.

Show the user the built file and ask them to approve the tone, depth, and look. This page is the style anchor for the rest, and fixing it now is far cheaper than after twenty pages. Stop until they answer.

## 3. Full build

Write one file per page, `pages/NN-name.json`, then add it to `guide.json` and run `--check`.

One agent working in order gives the most even voice, and is the default. To go faster, give each helper exactly one page file. The agent that owns `guide.json` also owns the order, the page ids, and any numbering; a helper cannot see the whole and must not edit that file or a sibling page. Its brief needs the page's plan entry, its sources, the first page as a style reference, and the block catalogue.

After each page, check that it does its planned job and connects to its neighbours. Fix problems before starting the next page.

## 4. Final review

Run the three views in `references/review.md`. If you can start an independent reviewer, give it the plan and the page, not your conclusions. Otherwise do the views yourself, item by item.

Fix every failure with the smallest edit, rebuild, and check the fixed part again. Report to the user only after that: what the review found, what changed, and anything left open. Passing raw findings along without fixing them does not finish the task.

## Without a user

In an unattended run the plan and first-spread stops have nobody to wait for. Do your own check at each stop, record each decision in `assumptions`, continue, and say in the report that nobody approved the first spread.
