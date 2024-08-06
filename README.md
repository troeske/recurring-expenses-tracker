# LOVE-TO-EARN
This is the website for vocabulary learning: LOVE-To-LEARN (L2L): [LOVE-TO-LEARN](https://troeske.github.io/love-to-learn/). 
<br>
<img src="media/L2L_landing_page_book_loaded.png"  width="300" height="auto" alt="Love-To-Learn Landing Page">

I was inspired to implement this site after helping one of my daughters to learn English vocabulary focused on certain topics (in her case crime & punishment and UK disparities) for her high school exam 3 weeks ago. Though she has successfully passed her exam already before I started the web app, it served as my inspiration and decisions on MVP functionality. With this past but real use case in mind I got carried away with MVP functionality and it turned into an NVP: Nice Viable Product with quite some complexity and advanced functionality. 

## User Experience

### Target Audience:
    anybody who is looking for a simple vocabulary learning app that allows manual entering and saving of vocabulary cards as well as opening existing exercise books. 

### User Stories:
    (1) 
    (2) 
    (3) 
    (4) 
    (5)
    (6) 
    (7) 
    (8) 
    
### Future Use-Cases
    (9) help with pronouncing the words correctly
    (10) saving learning progress beyond the current session
    (11) voice to text entering
    (12) more complex learning cards for flexible content (pictures, lists etc.) to facilitate learning any kind of content
    (13) ask user to save when leaving the page 

## Design
### Site Structure
The site implements a simple structure with one landing page 

### Program Flow

<img src="media/L2L_landing_page_I.png"  width="300" height="auto" alt="Landing Page Card Front - index.html">
<img src="media/L2L_landing_page_II.png"  width="300" height="auto" alt="Landing Page Card Front - index.html">


### Color Scheme
Black and white with highlight colors in terminal window.
        
## Current Features:

### Landing Page
The landing page is the core of the Love-To-Learn Site. It shows everything the user needs to get started with the learning experience.
<br>
<img src="media/L2L_landing_page_book_loaded.png"  width="300" height="auto" alt="Love-To-Learn Landing Page">


- __Username__
To make the experience personal L2L asks the users for their Name or Alias. 
<br>
<br>
<img src="media/L2L_username_scrn.png"  width="300" height="auto" alt="Username entry">

If the user decides not to fill in any data, L2L selects a default:
<br>
<img src="media/L2L_username_Incognito.png"  width="300" height="auto" alt="Hello Mr./Ms. Incognito">

- __Exercise Book Details__
This area shows the Name of the Exercise Book, the current topic within the Exercise Book and the languages to be learned.
<br>
<img src="media/L2L_book_topic_section.png"  width="300" height="auto" alt="Exercise Book Details">

### Word Card
- __Results Area__
The results of the current learning session is presented below the Word Card:
<br>
<img src="media/L2L_results_area.png"  width="300" height="auto" alt="Results Area">

### Navigation Bar
The Navigation Bar provides buttons to manage Exercise Books and acces to the Help/Info function.
<br>
<img src="media/L2L_nav_bar.png"  width="300" height="auto" alt="Navigation Bar">

- __Info Button__
The Info Button displays info on each of the buttons of the L2L Site. <img src="media/L2L_Info-Button.png"  width="30" height="auto" alt="Info Button"> One click on the Info Button will show the Info/Help text for each of the main site elements. When pressed again the info will disappear again. 

<br>
<img src="media/L2L_info_button_card_front.png"  width="300" height="auto" alt="Site Info - Card Front">
<img src="media/L2L_info_button_card_back.png"  width="300" height="auto" alt="media/L2L_info_button_card_back.png">

- __Save Exercise Book__
<br>
<img src="media/L2L_Save-Button.png"  width="30" height="auto" alt="Load Exercise Book">
<br>
At any time, the user can save the current Exercise Book. The browser treats this as a file download and on mobile it is typically saved to the DOWNLOADS directory by default.
(on mobiles it typically is saved to the DOWNLOADS directory by default)
<br>
<img src="media/L2L_save_Book.png"  width="300" height="auto" alt="Load Exercise Book">


- __Download Template__
<br>
<img src="media/L2L_Template-Button.png"  width="30" height="auto" alt="Download Template">
<br>

To make it easy to build your own Exercise Book, L2L provides a template download function. Save the file at a destination of your choice (on mobiles it typically is saved to the DOWNLOADS directory by default). The user can open the file in a text editor or spreadsheet program to manually enter word pairs.
The Load Exercise Book function allows the loading of the downloaded template into L2L and the user can use the L2L __Add Card__ function to add words as desired.

- __Load Exercise Book__
<br>
<img src="media/L2L_Load-Book-Button.png"  width="30" height="auto" alt="Load Exercise Book">

Users can load their existing (or previously saved) Exercise Books into L2L to start learning right away.

### Learning Mode
The core of L2L is to help user learn vocabulary. After loading an existing Exercise Book or manually entering a desired vocabulary the users can get start to learn and test their knowledge and progress.

- __Navigating the Exercise Book__
<br>
<img src="media/L2L_Card_Front_non-empty.png"  width="300" height="auto" alt="Card Front">
<br>

The top of the front of the Word Card has buttons to step forward (Next Button) or backward (Previous Button) in the current Exercise Book and shows the current position in the Exercise Book. The Front also shows the original word to be learned.

- __Learning and testing your knowledge__
To learn the card, the user clicks on the flip card button and can press on the magnifying glass to display the translation of the original word.
<br>
<img src="media/L2L_backside_enter_translation_empty.png"  width="300" height="auto" alt="Card Back">
<br>

- __Verifying your Result - correct__
Once the user has mastered the word, they can either type in the translation in to the input field and press ENTER (or the Enter button). If the translation was correct, the card will turn green and the 'got it' counter increases. 

<img src="media/L2L_translation_correct.png"  width="300" height="auto" alt="Correct Translation">

- __Verifying your Result - incorrect__
If the translation was wrong the card turns red and the 'to improve' counter increases.

<img src="media/L2L_translation_wrong.png"  width="300" height="auto" alt="Wrong Translation">


The user can also keep the translation in mind and just click on the magnifying glass to see if they were right. If they were correct, they can press the correct button below the input field. The card will turn green and the 'got it' counter increases. If they were wrong they can press the x-button below the input field and the card turns red and the 'to improve' counter increases.

The user can also flip back to the front and look at the original word again.

### Add a Word Card
<br>
<img src="media/L2L_add_card_front.png"  width="300" height="auto" alt="Add Card Front">
<br>

The user can manually add words to the current Exercise Book or start a new Exercise Book from scratch. To add words, the users clicks on the + Button on the front of the word card. When hitting Enter or clicking on flip-card, the card will turn to the backside and the user can enter the translation. L2L will save the card once the user hits Enter, clicks the Enter-Button or the Correct-Button below the input field for the translated word. Automatically the card will flip to the front to get back into learning mode.

### Delete current Word Card
The user can delete a card in the current Exercise Book by clicking on the trash button below the original word on the front of the card. A confirm/Cancel message will pop up and the card will be deleted.
<br>
<img src="media/L2L_delete_card_message.png"  width="300" height="auto" alt="Delete Card">
<br>


## Manual Testing

__Various Browsers on desktop devices:__


### Open/Known Issues
__Merge manual Cards when loading new Exercise Book:__

    (1) 
    (2) 



## Code Validation
### W3 HTML Validator https://validator.w3.org/nu/#textarea
__Results:__
All html pages were checked by the w3 html validator, and no errors remain.
<br>
<img src="media/L2L_HTML_validator_results.png"  width="300" height="auto" alt="W3 HTML Validator Results">
<br>

### CSS Validator https://jigsaw.w3.org/css-validator/validator
__Results:__
All CSS files were checked by the w3c CSS validator and no errors remain. Remaining warnings are due to the use of CSS variables.
<br>
<img src="media/L2L_CSS validator_results.png"  width="300" height="auto" alt="W3 CSS Validator Results">
<br>

## Deployment
This section should describe the process you went through to deploy the project to a hosting platform (e.g. GitHub) 

The site was deployed to GitHub pages. The steps to deploy are as follows: 
  - In the GitHub repository, navigate to the Settings tab 
  - From the source section drop-down menu, select the Master Branch
  - Once the master branch has been selected, the page will be automatically refreshed with a detailed ribbon display to indicate the successful deployment. 

The live link can be found here: https://troeske.github.io/love-to-learn/  

## Credits
### Tutorials
no tutorials were used.

### Code
W3Schools: https://www.w3schools.com/
MDN Web Docs: https://developer.mozilla.org/en-US/
GeeksForGeeks: https://www.geeksforgeeks.org/

Github Copilot provided the core of following functions:

    (1)  the upload/import of an existing .CSV file (incl. handleFileSelect(), csvToArray() )
    (2)  the 3D flip card design and animation (incl. respective code in DOMContentLoaded EventListner)
    (3)  drawDividerBack(), drawDividerFront()
    (4)  the convert array to CSV conversion: convertArrayToCSV()
    (5)  basic structure of editH2Content() (especially the ***.childNodes[0].nodeValue solution)
    (6)  the basic structure idea of a modal dialog of the greetUser() function 

I used https://tabletomarkdown.com/convert-spreadsheet-to-markdown/ to convert my Google Sheets manual testing matrix into a to table for this readme.

### Graphics
icons: https://fontawesome.com/
favicon: https://www.freepik.com/icon

### Photos

### Any other resources
https://validator.w3.org/nu/#textarea
https://jigsaw.w3.org/css-validator/validator


## Creating the Heroku app

When you create the app, you will need to add two buildpacks from the _Settings_ tab. The ordering is as follows:

1. `heroku/python`
2. `heroku/nodejs`

You must then create a _Config Var_ called `PORT`. Set this to `8000`

If you have credentials, such as in the Love Sandwiches project, you must create another _Config Var_ called `CREDS` and paste the JSON into the value field.

Connect your GitHub repository and deploy as normal.
