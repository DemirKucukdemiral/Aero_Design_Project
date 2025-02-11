# Git Commands

Please use this as a guid in using git gub and its commands


## Cloning

### Making a Token


Before beginning to clone please first ensure you can. If you have 2 factor authentication on you will have to generate a new %token% which is used as a password later on.

To create a token:

1. Log in to you github account.

2. Press your profile photo and go to *setting*.

3. From the left hand side scroll down to *developer setting*.

4.	Click “Personal access tokens”.

5.	Select “Tokens (classic)”.

6.	Click “Generate new token” → Select “Generate new token (classic)”.
7.	Give your token a name (e.g., "My GitHub Token").

8.	Set the expiration date (Choose “No expiration” if you don’t want it to expire, but it’s recommended to use a limited duration for security reasons).

9.	Select the required scopes: Repo, Workflow

10.	Click “Generate token”.

11. SAVE YOUR TOKEN!

---
### Cloning

To actually clone you need to first go find where to actually clone it and potentially make a file to clone into.

We can go to a directory (location in you laptop), by using the 'cd' command in the terminal. For Mac, going to your Desktop is done by:

    cd /User/name_of_user/Desktop

Now we can make a new 'GitHub' file using:

    mkdir folder-name

We can go into this new directory (file) and clone the repo here. Go back into GitHub and to the repo you want to clone. You will see a blue '<> code' icon press it and copy the HTTPS URL:

    https://github.com/DemirKucukdemiral/Aero_Design_Project.git

Once copied, go back into the terminal and go into the new directory and clone the repo:

    cd folder-name
    git clone https://github.com/DemirKucukdemiral/Aero_Design_Project.git

This should clone the repo into the new folder we made

---
## Using GitHub

GitHub uses branches, what this means is you can work on a part of the repo unrelated to someone else and when you are done you can merge into the main branch and barely anything will conflict.

For simplicity we will use 3 branches:

- main
- dev
- individual

main will be the final step and so should never conflicts. Dev will be the intermediate step where people works are merged into so that if there are any conflicts we sort them at this stage before merging to main.  Lastly the individual branches are what people work on they will create this themselves and when they are done merge inti the dev branch.

## Branching

At any director we can see the existing branches using the command:

    git branch

This should give you a list such as:

    * main
      branch_1
      branch_2

Where the (*) indicates the current branch. To switch to a new branch you could do:

    git checkout branch_name

Or,

    git switch branch_name

### Creating a Branch and Merging

---

To start working on your part please first make a branch and do everything from there. Ideally make the the branch from the dev branch.

    git switch dev
    git checkout -b name_new_branch

When you make your edits and push the stuff onto the new branch. 

    git add .
    git commit -m "commit message"
    git push 

Now when you are comfortable with your part, you can merge onto the dev. Start by switching to dev.

    git checkout dev
    git merge name_new_branch
    git push origin main

## Issues, Errors and How to Fix Them

### "Git Not Recognised..."

This just means you dont have git installed, just go and donload Git, (not github). When you do go onto terminal and do:

    git --version

This should give something like:

    version 12.x.x











