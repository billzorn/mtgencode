box_width = 350
id_lables = ["white", "blue", "black", "red", "green", "multi", "colorless", "lands"]
html_prepend = """<!DOCTYPE html>
<head>
    <style>
	    ul {
		    list-style-type: none;
		    margin: 0;
		    padding: 0;
		    overflow: hidden;
		}

		li {
		    float: left;
		}

		li a {
		    display: block;
		    color: white;
		    text-align: center;
		    padding: 14px 16px;
		    text-decoration: none;
		}
	    .card-text {
	        display: inline-block;
	        width: 350px;
	        margin: 2px;
	        padding: 3px;
	        border: 3px solid #000000;
	    }
	    #red > div{
	    	border-color:red;
	    }
	    #blue > div{
	    	border-color:blue;
	    }
	    #green > div{
	    	border-color:lawngreen;
	    }
	    #white > div{
	    	border-color:yellow;
	    }
	    #multi > div{
	    	border-color:gold;
	    }
	    #colorless > div{
	    	border-color:lightgrey;
	    }
	    #lands > div{
	    	border-color:darkgoldenrod;
	    }

	    div.hover_img {
	    	position: relative;
	    	display:inline-block;
	    }
	    .hover_img a {
	        position: relative;
	    }

	    .hover_img span {
	    	position: absolute;
	        display: none;
	        z-index: 99;
	    }
	    .hover_img:hover span {
	    	display:inline-block;
	    }
	    
	    .hover_img span p {
	    	padding: 10px;
	        width:250px;
	        background:#FFFF99;
	    }
	    
	    .hover_img img {
	    	height: 445px;
	    	width: 312px;
	    }
    </style>
    <style type="text/css">
    
	    .mana-0 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        ;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEvSURBVChTY/gPBn///nn57PGNy2cvnj4CREAGkAsUhMiCFP348f36pTMXTh2eOXWin6+Pk6NDZ2sjkAsUBEqBFAGVQ1QsXTDbxsb69LH9u7dtkJGV625vhqgDKmAAGgvkAJG9vV1bcz2EnZGWoqqqdv7kISAbqIABaD2QdWTfDj4+gWUL50AUTZnQw8PLv2ntciAbqIAB6Ewga/H8WXBRIFq1bAGQO3/2NCAbqACqCMgHiq5ethCiaO3KxUDu4nkzoYog1m1etwIoOn1yP0QR0BO8fAIH92wDskHWwR2uqamVnZkOYQN9YGNtDWGDHA4Pggk9HfIKikAfnDtx0N7ODmIXNAiQA7OrvdnXxzsiLHTapD6ICmhgAjEQAJUDjQVaD3QmEAEZQC5QECT3/z8A05MwgYZeWs0AAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-1 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAADjSURBVChTjZGxDgFBFEXHE7MrthFClBrNRvyTSET4CBIaCo3GT4jCT5AoNRoJdtcK0bFjY9dlZnXErd579+TNzJ1YGIaMsSB4nFzncj4K74ZW05PpTC6bLxDF0b4gIbzNeuXdrs7BnS+W9sFt1qsSLZZMTdMJO0Bgge/7k+lsOBrvLRsEhCEsAIRT5BGc81ajVimbkpCCBYBwDzV4yzBSqooEgOSaHwJAqvwpwhNU+UUACHmoLpJM7iMAhMQ+y2BbtrPdWUHEwXpHSvFXYnpSiHunN0DPeaLd7aPFEBaAP76FsSe9yn/QI2WYAgAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-2 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFPSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpTed+Dwuk1bf/z4aWttERsZysnFraimzc7OwQQ0A6Ji+669y1at8/FwMzLQmz1v8ez5i4GCQCmgAhagLUDOr1+/tu3YM6W/g4OdHWj+3Xv39+w7lJ4cD5QCKmACugMo+uPnz9ysFIgKIBAVEeHl4YGwgQqYgGqBLD5eXjUVZYjo589fDh89HhbsD+ECFTBBWHDw+8+f+pbOAD9vDzcnqBADAxPQt1AmKCD+dfRMcnN2TE2MgQqBg4MJGB4QDjAspsyY6+3hAjHj3IVLDx89ATKAChj//v1z6+qFH9+/9U6cBnQ+0P9AiffvP6zftG3JvGn8AoJq2gYswDAFhtiGNSuvXLsBlL5z9z6QBAIzE0OgCqAUUAER0cLAAAAj1rLKRkR9sgAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-3 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFUSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpQ+efrc2g1b3r57Z6ink5oUx8fPr6imzc7OwQQ0A6Jiw+btG7dsj48OC/L3WbFmw5btu4CCQCmgAiagLRAreLi5WhuqtLU0PN2cODk5RISFgIJAKaACxhuXz/74/g3Ih4Dfv39Pmjabj48vNTEGIsLBycUCMQYC7t5/0Nk7+dWr11+/fRMU4A8J9AUKAhUwXjx9BOJBIHj1+g0vDw8HB3v3hKnbd+zZvHYpDw83IyMjE9C3EBVAICYqAnQNUNTN2eH3nz9v3r4FCgIVMAHDA6ICGdy//1BQQEBGWgrIBipgAoYYUC3QxucvXkJUnDh1Zt6i5dXlBSwsLEApoAJoYF69eGb6jDmfv3z58vUbHy9vZFignKwMUAUkMImIFgYGALORsD4EQl2jAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-4 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAE3SURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpEGcpvbe9nY2CpK8oBKFdW02dk5mIBmwFUAwfpNW48cP/nk2TMgGygIlAIqYALaAlfx5Omzu/ceqqkqQ7hAAJQCKmACugPC//fv38w5CzNTEyBcOAAqYIIbs3TFWk93Fx4ebggXDoAKmCCsO3fvP3/50srCFMIFgrPnL756/QbCZrxx+eyP79/aeyZ+/vyFm4sLKHTy9Nl/////+/tv2YIZAgL8HJxcjC+fPX7+5MHHj5++fYfaW9/SBSQba8okJcSBDEkZBSZgiAHDg5+fDygERBLiYj9+/Pj06TOQAVQBlAIHKRMzKMQ4OEGGMDC0dPYDhTg42IFBCglMoAIiooWBAQBwdqfO6tnExwAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-5 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEpSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpRu6ez7+vUbUBQIfv36NWVCt6KaNjs7BxPQDIiKV6/fvHz5WkJcDIIszEyAgkApoALGl88eP3/yAKh1z/5D/Hy8psaGEJPgQFJGgQXoDgjn0uVrFy5dfvT4qZCgQHCAT1R4MCMjI1AcqIAF4lIIiIsOFxURPnDo6PTZC/7++xcXFQYUBCpgvHj6CMSDyKCyruXajVsbVy0CsoHmMQF9C5FABloa6h8/foKwgQqYgOEB4SCDazduaqipQNhABUzAEEM27PefPwuXrjx3/lJeViqQC5QCKkAEZntX/7fv396//yArIx0eEiApIQ5UAQlMIqKFgQEAnxOfpbljyQoAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-6 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFgSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpF+9frN2vWb33/4GBcdrqyspKimzc7Owfj3759bVy9AVBw5dnLuwqWlhTlaGmpALhAAjVTTNmB8+ezx8ycPgPx79x9m5pXOnzVJSlICogICJGUUGG9cPvvj+zcgp7KuhYWZWV9P58q1GypKCuGhgawsLEBxDk4uJohFv//8OXHyzI1bd2SkJYP8vVeu2dg3cTrIHAYGoAImCOvdu/dAdSkJ0RZmJno6WoH+Xtt27vnz5w9ElgnoNCDFxQkiGRgZQSQDg4Kc7N+/f9+9/wBkAxUwAcMDyOLl5VFRVrxx8zZYDcOXr9+4ubiEhQSBbKACJmCIQQzLSInfs+/Qm7fv/v37t2vv/qjwIGZmZqAUUAFKYB47cWrL9t2MjIzamuqRYUFAf0EDk3C0MDAAACK6pimZEg74AAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-7 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEVSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+62tM/+fGTZ8zMTEBRCCgpyLF2cGFn52ACmgFUATTgwKGjHBzsEuJiEHT7zj0ODjagFFABC9AWoIr3Hz64OjtkpMRDzDh4+Ji4mCg3FxdQCqiA8cblsz++f4PIQcCfP39SsgqnTeji4uIEcjk4uZggLkUGew8cVlNRhqgAAqAChDPhYNnKtc6OdlAOGDABfQtlgsGlK9cePXqir6cN5YODgwkYHlAeGOzcvV9bS4ODnR3KZ2AAKmAChhiyYWfPX1RVUYJywMaAg5SJWVFNG66Oh4dbSVEewgYKAqWACoiIFgYGAIXReK4bpsD6AAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-8 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFrSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6+v3b1+Wr1t24defnz5/aWhqRoYG8fPyKatrs7ByMf//+uXX1AtCAvkkz/vz9U1KQ/e/v396J03/9/l1bUQQ0Uk3bgAloC8SKo8dPamuoMzEysrCwuDrbX712HSgIlAIqYAK6A8gBAg111RlzFu7Zf+jv37+79x709nCDiAMVMF48fQTi9i9fv7Z09B05dpKTk8PJwbayJB+iiJGRkQnCAoKHDx///v27oaZMR0tz6/bd8xYtg0oA1d24fPbH929//vwJDE/obKnV0lQHigK9OXPuoh2bVnIA/cbJxQQMD6Dop0+f33/4ICYmCtbJEB4aCPTjt6/fgGygAiZgiAEVCwkJ6mprrt+0DaLoxMnTBvq6QEGgFFABIjDfvXu7aOmqN2/f8XBzcXBwxEWHCQkJQwOTcLQwMAAAqCC9xuBqHPkAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-9 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFeSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6+uP7t+Wr1l24dIWZmdnfx8PCzASoVFFNm52dg+Hv3z/XL525cOpwUUGulaXl2eMHdmxeKyUlM2vaJKAgUAqogAloC9CKf//+AY1xc3EEGiMhLubqbD9jzgKgRUApoAImoDuAnDdv333+/IWPlwfIBgItDbVbt+9+/fYNyAYqYIK4VEhQAGjGw8dPwGqATmUEEl+/ghQBFTCBxRhYWFi83F02bN5+/ebt02fPz5m/BCgiwM8HkWUuyMv+8+c3kGVuZvz71++Dh4+xsrL+//dPTFTU090ZKM7BycX48tnj508egDVAwes3b+NSsid2t6qpKgO5kjIKTMAQA4YHRBoIbt25W1nXUlaUC1EBlAIqQATm3bv3Fi9fxcfLG+TvLSkhDlEBCUwiooWBAQCs87JoDmJq4gAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-10 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAE9SURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcLEAzgCqOHT+x/+ARH083DXXV6zdv79i19/PnL24uDkClatoGLEBbgGZ8//5j6449zo52P378mDhl5tQJnUCR6KRMFWUlIRFxJqA7gMptrMylJSWAjMNHT8jJyjAzM/PwcGuoqezasx+ogAnuFBZWFiB56849bm4uiIikhPiTp8+ACpggfDj49u37v3//IGw2NjZ2dnYggwnoBYgQBCjIyz599gLC/vLli6qKElABEzA8IEKfPn3+8uWrq5P9rTt3P33+/O///3v3H9rbWgEVMP79++fW1QsTJk07eeacmKhIamLsx0+fdu87KMDHB/SNiYkxMAiICkwiooWBAQCBlamF9Pj2KwAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-11 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAD0SURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcTEAzgCoePXq0ccv2tq4JQLmnz56vXLNh+qz5QG1AKaACJqAtQA4jI+OVqzdu3bkLVMTExHT2/KVHT54C2UApoAImoDuAHDFRETsbSyADCCQlxE2M9CFsIAAqYMJ0ChoAKmCCMvECJqAXoEwcAKiACRgeEM73HyAAYf/+/fvr128QNlABc2dX98f3b69du7F2w+afv359+fL19+8/23bu/fL1Kwszi66ujqyiKlGBSUS0MDAAAJsNl49choAcAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-12 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEySURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcjH///rl19cLly1cOHz1hamKop6P16PGTNeu3MDMzhYcEyMvLq2kbMAFtAZrx+s3bFWvWf/z46c3bd9NnL7C3tfz582decRVQCqiABegOoMnWlmbSUpJAxsnT58qLcgUE+BUV5Ddt3fnp82eOt6+Y0Jzi7eECVAFk3Lh5S1dHi4+XF6iACSKHBp48fb5y7cbGmjIIlwnoBQgLDl69frNm/ab2xhphIUGgK4EKmIDhAZH79u3716/fPnz42DtxmpWF2c3bd6bNmn/vwUOgAmgQzFu45MrV61xcXCzMTE+fv4BoY2VhndTXoaVvQlxgEo4WBgYAuEeubJyWa+YAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-13 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAE1SURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcLEAzgCrevH594dKVr1+/ebg5ff/+Y+2GzU+ePnd2tAUqVdM2YALaAjTjxctXC5euvHn7zq9fv3omTNXUUDM21KtpaAdKARUwAd0BVK6qomRlbgpksLKyFudnGRvqc3FxOdrbAEWACpjQnMLIyMjBybF42eqOnkl///4FWg1UwASVRAJMjIye7s7rVi54+PjJlu27QCJAL0DkkIGIsBArC4ucrDTQ70AFTMDwgEh8+/bt7bv3v3//BloB5J4+e/7uvQde7i5ABYx///65dfXCgYOHt+7YDXSEpbnp5y9fPn36zMfHG+DrKSQkDAwCogKTiGhhYAAAExGx/k7dMTQAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-14 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEuSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcTEAzgCoePHiwet2ms+cvQuUZGLbt3LNl63agFFABE9AWoBlPnj5buHTly1evISru3L2/eevOazduAaWACpiA7gCKmhobammoQVT8/v17zfrNYcH+EC5QARPcKczMIDcCweJlq4EqWFhYIFygAiYICw6uXrvx9+9fMVGR7z9+/PnzB+gyoCAL0As/vn+DqACCd+8/vHr9ZuLUWddv3AJyjQz1gQpYgOHx/MkDIP/Dx08fP37ycnextbYAcls7+5mYmRztrIEKmIAhBlS7YfN2AX6+W3fu3b0P0nD56nWgCiDj5u17QAVEBSYR0cLAAAAOyLDdh7oV9AAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-15 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEySURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcjH///rl28cyuPfv27DuYnhynIC83efqcZ89fABV9/PhpYm+Hkbk1C9CW379+srOxHTl2Miku6tevX3/+/AkL9gcqYmJiYmVhAipgAroDyLGxMufm4gJKXL95++fPX0ANL1++1tXWBIqAFKA55fGTp/z8fGKiIrPnL+7smwwUASpggcjBgY+nG4Shq6OVnlOcm5HCy8vDBPQCRBQNSIiLAT3+7/8/oAImYHgAhf7+/fvr9+/vP35AVAClFy9bZWttwcfLC1QACoIr50939k64dv2mtJSkiaH+i5evXr15KyMlGRMZysfPr6ZtQFxgEo4WBgYA5PenFhKZDwsAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-16 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAE7SURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcTEAzbl+7uGv33prG9jdv30GkT54+O2XG3EOHjwI1AxUwAW359fMHEBw4dPT3799AFQuXrjx34XJWepK5qRHQeKACJqA7mJmZ3V2dIGbcuXt/5+79Lo52p06f/fXrF1AEqIAJzSk79+wHyl25duPQ0ROFZbUgF//4zgSVhIHXb94CTQ308yrITrt2/ea9+w+BgkxAL0CkIUBURPj7d5DZbGxs3Dzcf/78ASpgAoYHUOj3nz9A8vOXLx6uTsdPngFyX7x8xcHOrqSkAFTA+Pfvn/Onjk2cMv3y1esKcrIFOenXbtw8cerc379/Q4N81dXV1bQNiApMIqKFgQEAeKDC4O/kvu0AAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-17 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEqSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcjH///rl+6eyZs+d27NqXn5124tSZ3fsOcnNxQdQVFWSbWdkzAW358f3btes3t2zf9ffv3xOnzxrq69rZWALR23fv2FiYgQoYb1w+C1T0798/O1e/HRtXvnn3TkFOFmjG4aMnfvz44erswMHJxQRxChMTE9h4BogKoENXr9vkYG8DZAMVQOXQwOmzFyQlxVlZWCBcJqAXICxksHHLdlMjAwgbqIAJGB5A1sePn4DkBzAJdN/xk2c01FVBShgYgAqYgCH25+//hUtX2lpbrF638ffv358/f9HSVBMTFQGqABoDVEBcYBKOFgYGALrIn9uhneDtAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-18 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFCSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcLEAzgCquX79x+NgJDTUVc1Pjw0dPXLx89efPny5O9kClatoGTEBbgGa8ev16+ap1b9+9v3LtxqatO3IykjNTE9u7J3788B6ogAnoDqByCzMTFWVFIOPdu/fPn78Ekhwc7Dw83AyMjEAFLGhOsbEyP3HqTEh0soKcbE5mMgc7O1ABE1QSBj5++vT9x8+m2nIhIcGuvsk/fv4ECjIBvQCRhoD1m7Zpa6oDzetuq5eSlLh46QpQARMwPCDS3759//nzl7iY2M1bd4BcRkZGFhYWGWkpoALGv3//3Lp6YdbcBafPnufh5k6Kj7px4/bzly9ZWVj19bStLC2AQUBUYBIRLQwMAOBQr7aPizrUAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-19 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAE8SURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcLEAzgCouX7ly7PhpQUF+fx/Pq9dubN25h+H/fx8vd6BSNW0DJqAtQDOYGJl27tn/9u37799/1DZ1ZKTEpyTG1ja2v3zxAqiACegOoHIVZUUdLQ0g4/zFS/z8fHy8vEKCAqoqSgcOHwMqYEJzChMT0/v3HyBsbi6uV69eg+yB8OHA2MiAk5Nz1txFq9ZuPH7yjJCQIFCQCegFiDQEsLKwzJ7Wp6GuaqCnw8LCbGdjCVTABAwPiPSPHz++//gBZPBwc1tamK7ftC0jNUFMVASogAUYYu/evNy0eeunz1++ff9x5tyFz5+/XLtxy9vTFegVoDFABUQFJhHRwsAAAEKMo0bborQ8AAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-20 {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFjSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcjH///rl19cKxYydmz1/87///1MQYU2PDHbv23Xvw8PmLlxmpiR4+AQwvnz3evmlNcGDAvp2bm+qqRUTFN6xe6uvtdeHU4RWL5xkYGAAVMAHd8fjJs8LcDCFBATdXxx8/fmzYvF1DQw1onbqayqtXb86ePc0EdIqZiSEPDzdQFGiLu4vj+/cfODnYgVxGRkagzmdPnzGBXAgGFy5duX7zVkVpPhMz848fPyGCTMxMvDw8TEAvADnXrt+8eOlKRXHer1+/uDg579y9DxQE+gPI1dbRYgKGx937Dzr7Jv/9+2/ewmUllQ3enq537z149PjJvv2HAvy8RcUkQUGwYsmiq9eugY1nYGVlDfTz+vjx04HDRyXExexsbdS0DYgLTMLRwsAAABnzwHeRF3aFAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-2-B {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAF8SURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/Th8/vHrtej0dLRMjA6AoBACVyitrcHJxMwHNuH/r6vqNm3083abPXvD792+oEqDxf/9ePXPs79+/TEBbgFZEhwcLCvCLi4mysLBAVLCysr19/vT71y/PHtxlAroDKMTIyLhq7cbC3Ix///7BVYAVM7x+/pgJ4tLO3kk/f/2au2Dpq9dvgCpWLF+5Yt3mG7fvAqW+ffnCePH0EaDbb9+5B+QzMTFpqKvVN7YeO3X20+cv3FycRVkpVmYmTEAvAKVVVZSACKjixaOHv379CvLxADouPz3pyo1bXDw8TMDwACoCAog7WFlZJMXFzl28oqelceLseWUFeVFJWSZgiAENQ3ZpdGgAMzPT12/fgCq8PVylFJRBgfnj29crZ44BfQtRBATXbt7m5ub6x8AUGh0PDExotABDDBgeQN8C/QLkAt0BtAVoBjMzMwMDAwArqbIv/yKO/gAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-2-G {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAF8SURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/Th8/vHrtej0dLRMjA6AoBACVyqio8XDyMgHNuH/r6vqNm3083abPXvD792+oEgaGz4zfdtzY8ufvHyagLUArosODBQX4xcVEWVhYICp+cf6/9Onqx+8frz6/zAR0B1CIkZFx1dqNhbkZ//79g6sAK2a4++Y2E8Slnb2Tfv76NXfB0lev33xj+b1i77ot83c8uvUEKPXx+wfGi6ePAN1++849IJ+JiUlWW76lr3vfmkNALjMLc35fpoK6HBPQC0C+qooSEAFVAG05seM0UJqbjxsovn/tIX5OASZgeAA5QABxB9BUeU05EyfDH99+RBQGG9rrK4uoMgFDDGgY3KVAH6Q2xIvJirKysQgI89s6W2lL6oIC8+uPL9uvbwb6FmIkEPz6+fvLhy+S4lJ+RgF8HPzQaAGGGDA8gL4F+gXIBboDaAvQDBZmFgYGBgCzOLYQy2aUMQAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-2-R {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAF2SURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/Th8/vHrtej0dLRMjA6AoBACVqigqs/AIMAHNuH/r6vqNm3083abPXvD792+oEgYG3u/v/u2ZzfDnFxPQFqAV0eHBggL84mKiLCwsEBUi/7+L3Njz/9Obv9ePMgHdARRiZGRctXZjYW7Gv3//4CrAihn+3r/ABHFpZ++kn79+zV2w9NXrNyL/vr3at2rbpQcfv/8CSv3/9Jrx4ukjQLffvnMPyGdiYjJXFL++aeGn7792X3n05P2XhgALHTkxxhuXz/74/g1kLpItzz58ffD605S9F8X5uSZkhjEBwwNNxdxDV/VqlrRvPX375QcjOVFmRQMmYIgBwwPZpa8/gwy+9PiNpqSgpooSs6Y1KDD/fP34b/csoG8hin79+bv5wn0mRgZLA225kHxGXmFotABDDBgeQN8C/QLkMfKBbAGawcDCxsDAAACkY8S0HdMPswAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-2-U {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFmSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/Th8/vHrtej0dLRMjA6AoBACVyqvpcrKzMQHNuH/r6vqNm3083abPXvD792+oEgaGP2x8F158+/vvPxPQFqAV0eHBggL84mKiLCwsEBXMfOIvmYS+/fr7+MMPJqA7gEKMjIyr1m4szM349+8fXAVYMcPLzz+ZIC7t7J3089evuQuWvnr9Bqji2utfR3ZthSj6+vsv1PCQQD8gycTEJKOm9/Qvb0thkLquoY2bN0SWCegFIKWqogREagbmQFv2bFx9/+a1PRtXPbh1HSjFzcrMBAwPsGqEOy6ePAIkJaTlLp85AWSI87IzAUMMaBiySyVk5YHk04f3gB7nYmOWFeAABeb3n7+A4QH0LUQR0CvbVi0BMkJi4s2VxDhZmaHRAgwxYHgAfQv0C5ALdAfQFqAZzEyMDAwMAPOdnxQjjxd1AAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-2-W {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAF9SURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/Th8/vHrtej0dLRMjA6AoBACVqmhos7ByMAHNuH/r6vqNm3083abPXvD792+oEgYGXn7O//9fAq1hAtoCtCI6PFhQgF9cTJSFhQWiQkRcSFSc7f//33//fmQCugMoxMjIuGrtxsLcjH///sFVgBUz/Pv7mQni0s7eST9//Zq7YOmr12+ERQUZmL7s33/i1y+Q1UDDGC+ePgJ0++0794B8JiYmEzP97z/flJZ3vn37IS013M7WTFpagvHG5bM/vn8DmQu2hYPrd1JyxbHj54DG2NmZzp/byc8vxAQMD7gKoDs4ONjNzfUFBfnZ2dnkZKUuXLjGxMzLAgyxd29eAn0LcSkrK0t0lN/37z9kZaX+/vljb2/NzMwPCsw/v3/+//8C6ECIkUDw6dMXPj6eP38YObnkGBlZodEC8unfj0DfQpQCJYC2AM0AeoaBgQEAtzarPAuf1fsAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-B-G {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGHSURBVChTY/z//z8DA8Pfv38f3L7+7uXzn9+/AblcPDyikrJSCsrMzMxALhMQf//2tb6y1NDc1j0ocvXGrf////v6+dODW1fPH933+dtHkCKgGQtnT9+x5wAHOxsjA+ORE6dv3L4LlACCH+x/d97c9ufvH+aUuOgjhw9rqiozMjFKiIt5uzq+ffdBWUGOUYjz5t8HP//8ZGVmZXr9/LGjjQUvL8+9B4+ePn/By8PtYm8NUQEx7+6b20zfvnxhZGRUkJORkZKUk5GSl5X5x8++/sTOLfN3PLr1BKjo4/cPjIe3bwC6FKIJCIBmdM+ctm/NISCbmYU5vy9TQV2OCehbiDQQQGw5seM0UJqbjxsosn/tIX5OASZgeCCrAAabvKaciZPhj28/IgqDDe31lUVUmYAhxsnNA3cp0H2pDfFisqKsbCwCwvy2zlbakrqgEP/y7dOOm1s/fgeFGwT8+vn7y4cvkuJSfkYBfBz80GgBhtjV55eBvgX6BcgFugNoC9AMFmYWBgYGAMLJqhxVea9iAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-B {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGPSURBVChTY/z//z8DA8Pfv3+fPbj7+vnjFy9eMDMziwKBpKyUgjKQDZRlACr69vXLqQM7i3IyxCUkeXj5gUhRQbEwK/30wV1AKaACJqAZV04frWpsf/r8xdev30D6GBhev3137PTZSTPmXD1zDKiABWjLhs3bTpw5z8fLw8bK+uv3b4i6qzduA5GOhpq4tDwT0B17Dx011NOOiwgWFRGGqBATFc5MjDE11Nu2ez9QAdO3L1+AhtcU5Xi5OLRUFzMyMgIVNZYX+no4VxfnPH/5CqiABaRPRGTJmg1y0lIfP31WVpR/9frN+ctXb929/+79ByEBAaACxrOH9zx/9uz46XNAdOrcxdjwIBZm5vnLVluYGFqZGQNtlJKWZgGGx9fPn9yd7ORkpICK3rx9x8nBAdSdnhAlLioCZAAVMAFDjJObB8j58vWbrLTksVNnDx47KSUh9uPnT6AgUAqogAkYptomVkAOJwe7oa62tZlxbmq8orzc71+/gYJAKaAC9GgB+gXIZWJllVVQgUYLAwMAd3S7M57KFFAAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-B-P {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFxSURBVChTY/z//z8DA8Pfv3+fPbj7+vnjL58+Xbhy3cbKXFRSVkpBmZmZGSgLUvT929erZ459//oFyL/38PH1m3e83RyBbE5uHm0TK04ubiagGXAVv3//OXDkxItXbyDGAwWBUkAFjI/u3Hxw6ypQ6O79RxNmLuDkYH/15i0HO0dxdrKqkjxQXEFNmwnoDiDr379/vdPmZiZGBXi7WpkaVRdlTpq18MfPn0ApoAKmb19AFl2+dktCTFRLXYWNlfXNu/ey0pL6Oho3bt8DSgEVMAEpIPjz5w8LC8gjnz9/FRUWAjKAqn///g2WZGDi4uEBUprqKrfvPrj34BEPDzfQ1R8/fT574YqyghxQCqgA4fCbd+73TZsrIyX59PkLoBNjwgLsLE2B4kCHMwItOn90HyQIvv/4sWbTDmAQpMaGCfDzAUWAQWVo7cQEDFNQiHGDLOXk4HCxtxIXFYarAEoBFaBHC9Avl67esDA3QUQLAwMA8Y7AP7Vm5bMAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-R-B {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGKSURBVChTY/z//z8DA8Pfv38f3L7+7uXzn9+/AblcPDyikrJSCsrMzMxALhMQf//2tb6y1NDc1j0ocvXGrf////v6+dODW1fPH933+9M7kCKgGQtnT9+x5wAHOxsjA+ORE6dv3L4LlAACwb9f/u+by/DnF3NKXPSRw4c1VZWZmJgkxEW9XR3fvvugrCAnxcEg8/gEw89vjCzsTK+fP3a0seDl5bn74OHT5y94ebhd7K2hKsDg7/0LTN++fGFkZFSQk5GRkpSTkZKXlZHiZPh0ctu2Sw8+fv8FVPT/02vGw9s3AF0K0QQEQDPu71378duvPVcfPXn/pSHAQkdOjAnoW6g8WAXQFls1aSMFsTAzNTYW5rmHrzLyiTIBwwNZBZAx99BVvZol7VtP3375wUhOlFnRgAkYYpzcPMguff0ZFJ6XHr/RlBTUVFFi1rQGhfjvz+//753z/9MbiKJff/5uvnCfiZHB0kBbLiSfkVcYGi3AEPt7/SjQt0C/AHlAdwBtAZrBwMLGwMAAABgmq3sFycQFAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-G {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAF7SURBVChTY/z//z8DA8Ofv3+uPr9868WNy5euiEgIy0jJKIuoakvqsjCzAGVBij79+LjhzLqP3z7Ma1x85/I9NnZWK29zIXEh71APDx1vPg5+ht9/fs8/MEdUUkJASJiHlx8ZReSFrT63DKiACWjLs+dPv3/5/uf3H6DJyGDL/J2XL1wBKmC6+eL62umboMIMDEJigkBSw1gVwl3ev+b2y5tMz14+u3PxHpDPyMgoISf27tV7IPvLx29gNQwvHr568/EN05+ff5iYmYB8Ll5OMVkxiBzQdn5hPgj7zbM3LIL8QswsTP//M1u4m146dhVoHtC/cuoy9oE2QNef2XdeSUmJ8cLjc7vP7GRkYhQQ4b97+f7k0plA3dVzS0SlRSAmmciZMwFDTEFeHqgC6Luf339CJP7++Qth8HPyAxUwAA3/+P3D4qMLQrND9K0MRMTFhERERCTETRxMFh2eB5QCKkCJlkv3Lzx99pRXkIfhB5O1obWOlD4oWhgYALFwqFkPjXZZAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-G-P {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAF4SURBVChTY/z//z8DA8Ofv3+uPr98983t91/f3bpw19zaVFlEVVtSl4WZBSgLUvTpx8dd17d9/P4RyH967/mDa4+sfcyBbH5OfjdNLz4OfiagGXAVf37/Obf/4tsX7yHGAwWBUkAFjBcenzvz6CRQ6MndZyv617NzsL1/9YGdky2qJERWVRoobiJnzuwa5/Tj9/d///7NrF4Qku0npSTBysbqm+KxrHetiZMBMwvz99/fmT5+/wBUfvfSA2FJIUVteRZWlo9vPonLiqrqKz248Rhs6QcmIAUEf//8YWZmBjK+ff4mIMYPZLCysfz59QcsycDEzykApBS05B/dfvL07nMuXs7///5/+fD1xpnbMipSQCmgAoTDH918srRnDdCiV0/eAJ3oGediaKcLFAc6nPH3n98bLq2GBMHP7z/3rT4MDAL/NE9eAR6wMfwBeqFMwDAFhhiQAxRi52Q3dTESEheAqwBKARWgRwvQL7cv3jOxMEJECwMDAOLavZeFAemOAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-G-U {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAF6SURBVChTY/z//z8DA8Ofv3+uPr98983tj98/ALn8nALKIqrakroszCxALkjRpx8f1xxbuXb+Blk1GT0rHXZONqAEWCm/u6Y/LwcX4+8/vxcfWpDnXwKRMHUxii4Jg7BlBLX5uHTNZPmZgLbs2rCbkZGRmYWZi5fr9J5zH99+gqhgYdH69uvv4w8/mIDu4BXgtfQ05ebj0jJVjywMYWFlhqiAmPfy808moEvN3U1s/aw5uDjYONj0rLXV5c0+vhU6smsrRNHX33+Z/ZN9/zP85xXg0bfRVdZVVFcwZ2RQrc2I+ff3r4mtI1ARIyMDE9C3EB18QrzaKpasrFp7Nq6+f/Pano2rHty6DhTnZmVmAoYHRBHcHRdPHgGSEtJyl8+cADLEedmZgCEGDA9kl0rIygPJpw/vvXn5nIuNWVaAAxSYn39+u/LiF9C3EEU/f3zftmoJkBESE2+uJMbJygyNlr///gPDA+hboF+AXKA7gLYAzWBmYmRgYAAAmW+MFdMXf4cAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-G-W {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGASURBVChTLZHBS8JQHMff9jadm9ucRaSyHTIzULMws9LwFBGUXuqQHbsXUtQ/0Km/ontJHRUPQhcjiIQsIuncIYNmhaJb67de7/Qevw/f3/f7fZRlWQghwzQeXu9f2i29+wFP2eUJDocivhiDGXjaUKenl+pnpdNLLRSILUYcnAMGf6i8Fs1xrMCABhC7+QMymFtOFPY3yV3zjGKrjZCLhi2ViypFUZjBvMjfVG/19w4QMV942q9a1sA0dRp8SIq4sJp0y8JkIrRV3ACaEETvx/ykwWlqZXYplwYrLoGLZ6LzEzMBVqjVrvv9AUAghvM76xayRI8bxsHYWHJ8ymvgveJxuXLF85xX8UiSm4a0RFYekjLRZFgZOTw6qdfvms3n81JZFAWKYmnog0DEB8c5U6m4oshOp0NT/Y3GI41FBhprvT1BWuKUZZntQq7b7amq3zSMbDaNsWyX2Rt8Qx9gkEjC6XS+wIphUC5eg3X/32InNXVIS1DbBxZBAyEaIfQLv3eOqz+RRXkAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-Q {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEPSURBVChTY/gPBl+/fu3p6TUztxAUEgEiIAPIBQpCZEGK7t69a2BozMPLj4aAgkApoAJGoHJrG7s7d+4wgIGri4u9gz2Qe//+/cuXrwgJCR09cohZSEh43fr1EBVA4OnhXlNd5eXp+frNm4MHD7148YKHm5tp1erVUHlUADTsy5cvQAZQAdPt21CL4KClte3b9++ZGRkQLkgB0C9AN5pbWObm5QMZRsamQBJoEdC9EpLSQDZQAQPQtwKCwjdv3gSK7ty1KzAwGOgpoJP//fsnLiEFVARUwAAMDyBLTV1j27btQHVwsHXrNqA4EAEVoASBkaGhr6+PlLQ00OAZ02cAXaaiogIMAqICk4ho+f8fAP4Nu28tFPTdAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-R-G {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGBSURBVChTY/z//z8DEPz59ff60b/3L/z/9BrIY+QTZVY0YNa0ZmBhA3GBiv5/frult+rF8+cXHr0ucDOUE+YFaQMpFfnrksTJI8wENOP33nmizL81pYT0ZEUCJm1+8v4LRNFzPv6tt3f9+fuHCWjL/09vfvz+c/jW03uvPjIxMr748BWo4oWM8h6Ofx+/f7z6/DIT0B1AoYQ5u9o2n37w5tPff/9FeTkhKsDGMdx9c5sJ4lJbNWkg+fzj14nR9kw6epMuX98yf8ejW0+Agh+/f2D8sbiS4d9fIOff//8gu2SU85Zs2bfmEFCEmYU5vy9TQV2OCehbIB8IICqAtpzYcRoozc3HDRTcv/YQP6cAEzA8IIogKoABIq8pZ+Jk+OPbj4jCYEN7fWURVSZgiAHDA+5SRkbG1IZ4MVlRVjYWAWF+W2crbUldUGD++PJ2y+1dQN9CjASCXz9/f/nwRVJcys8ogI+DHxotwBADhgfQt0C/ALlAdwBtAZrBwszCwMAAABU4tE5ME7m/AAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-R {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGQSURBVChTY/z//z8DEPz59ff60cdnD7198YSTlUVZRZVFyZBZ05qBhQ0oCVL0//PbN5unda3cZawgxszENGHX+ZefvlX6mMa627A6JzHyCjMBzfi9d17Ngi0P3342kBMF6rNRk1qc5t619czMTQfOz28HKmCuDXX69/CSg4aMj4GSCC/nhnN3l5+4ZaEsef/Np43n7vEw/bXRUmT8ubHv/4cXIGfBwL///3/8/ps8b/eeq49YmZiuTyth+f/pNUTu/uuPN56/lxbkufv644azdyPN1V9+/Hbp8Ztf71+xQFQsP3GzYNnBv//APmVgqPY16995/vKTN0B7Rfm4mBj5RP/8+1ez9hhcRYGboa+BIlCFlAB3ta/pm/+cTMyKBt9//fn4/RdEBRBsuXjfZ8ImIIOPkw1onriBNRMwxPjEpLSkhCAqgODOyw/ywryRFurRlhoLCiNYNG2YgGEKDLFZOSFAw6GqGBg0JYXirTWzApwEvDOAChDR8vPKocdnD///8laQm4NPTBroDGi0MDAAAN4or3qfztnlAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-R-P {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFzSURBVChTY/z//z8DEPz59ff60b/3L/z58OrQzadO5obMigbMmtYMLGxASZCi/5/f/t477/+nN0D+lafvTt17mWSrCZLjE2F1TmLkFWYCmgFX8evP3zWn7zx8+/kf2HigIFAKqIDxz6V9f87vAApdevI2f+lhbnaWJ+++cLOzTo21N5ATAYqzGHowAd0BZP399z9r0cGOUMtMRx1vfYUFKc6Fy498+/UHJHX/AtP/T6+BrGN3niuI8JoribOzsjz78FVVXMBWTfLM/VdAKaACJiAFBL/+/GNlBrHff/0hLcgDZHCwsvz88xcsycDEyCcKpMyUxC88enP5yVsBLnagd998/rH32mNdGWGgFFABwuHnHr7OXnxQRVzg7quPf//9q/Q2DjBSAooDHc74//fPX1smQoLgy8/fk/dcAgZBc6C5KC8n2BgRNp98JmCYgkKMD+RbHnbWCHNVOSFeuAqgFFABerQA/XLk1jNbE31EtDAwAADyV7v/4UsLTAAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-R-W {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGDSURBVChTY/z//z8DEPz59ff60b/3L/z/9BrIY+QTZVY0YNa0ZmBhA3GBiv5/frult+rF8+cXHr0ucDOUE+YFaQMpFWH1SGfk4GMCmvF77zxR5t+aUkJ6siIBkzY/ef8FoohBRukP03sGhn9MQFv+f3rz4/efw7ee3nv1kYmR8cWHr0AFjFpmDLr6/////vv3IxPQHUChhDm72jaffvDm099//0V5OSEqwKYx/Pv7mQniUls1aSD5/OPXidH28rbOryVk9+8/8evXb6Ag0DDGH4srgYpBOv7/B9r1V8P4MZ9oaXnn27cf0lLD7WzNpKUlmIC+BaoAAqAKoC3fldTLyruOHz9/5cqtNWt38PJyMzKyMgHDA6II4g4ODnZzc31BQX52djY5WakLF64xMfOyAEPs790zQN9CXMrKyhId5ff9+w9ZWam/f/7Y21szM/ODA/PH5z9M74AOhBgJBJ8+feHj4/nzh5GTSw5oHSxagI7/+xHoW4hSsDt4gWYAncrAwAAAt/eqrK7r7XkAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-S {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAE4SURBVChTY/z//z8DA8OvX78e3r/z59eP3Xv2ArmuLs4sbBzyiipsbGxALkjRzx/fT5882tzeJyrE//HLN6AoPw/X63cfayuLTM2t2Tk4Gf/+/XPlwunde/a9//T96bNnsbExQEWLFi2WkZYW5ON0dXHSMTBlevbkUVh00ut3n+/cvRsaErJ/334gCgsNBXKBguExyUAFTJ8/vre1Nreyslq8aOHmzZulpKUlpaSADCAXKGhjZQZUwNhYX/Ps5dtv374JCAgwMjCUlZUBrevq6gJ658OHD1xcXFLiwkxAITyAkRGokYEpNDjw7+/vIcHBvT3dwIDYtHkzEAEZQC5Q8M+vb0AFTLz8gkeOnTp27FhsXLyvr++zp0+BCMgAcoGCQCmgAuxBsHjxEmkpKXgQEBeYhKOFgQEA/P7IQI/HNAMAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-T {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAEySURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRz58/7t+6CpFGBkClimra7OwcTEAzsKoAAqAgUAqogAloC0TFjx8/NmzePn3WfCD57t17oAiQAZQCKmC8cfnsj+/f/v79m5pddOv2XbARDCwsLM6OdidPn92ydikHJxcLxJgLF68AVehqa0aEBj549HjVmg07d+8Din/5+pWRkZEJrJPh67dvQFJfT8fe1kqQn//nz18Q8WfPXwBJFqAXgNYpKSoAOZcuXwXaa2piuHjeNLAaBmEhQaACJmB4ADky0pJ6OlqXrlw7e/6SpIQ4HLGxsQEVMAFDDKgWqC4zLRFofWtX/69fULuAACgFVIASmHMXLJWVlXZzdoCrgAQmEdHCwAAAflyrAjDm4ZIAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-U-B {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGDSURBVChTY/z//z8DA8Pff/8ff/jx5N2XXwxMQC43K7M4L7usAAczEyOQCxL6/vvvqccfm1tar9+4AdQCRF9+/b379htQ8Nv3HyBFQDMuPPt85MD+VXOmXD9/BigEByzfP1w7ffjv379MQFu+/fq7YuZEoOjaBTPevHwOUcH39/OP++e/f/3y7MFdppeffwKFHty+ASQ19I3OHN4PVwFSy8Dw+vljpq+//wJZJraOQPL0ob1ahiZAFZvnT16xbvON23eBgt++fGHce/sN0KV/fv++cemchIyckghPV2X+sVNnP33+ws3FWZSVYmVmwgT0LVA5CyurjrE5UMXnW6d//foV5OPBwsKSn5505cYtLh4eJmB4ABUBAcQdrKwskuJi5y5e0dPSOHH2vLKCvKikLBMwxLjYmJFdGh0awMzM9PXbN6AKbw9XKQVlUIh/+/Hz2qlDQN9CFAHBtZu3ubm5/jEwhUbHc3Jxw6Ll719geAB9C/QLkAt0B9AWoBnMzMwMDAwA1ATEGG+vZB0AAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-U {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAE0SURBVChTY/z//z8DA8Pff/8ff/jx8vPPr7//ArncrMzivOyyAhzMTIxALhMQf//999Tjj3fffvvy6y9Qy+GdW4EMIBcoCJQCKQKaceHZ52+/QBwgWDFz4r7NayBsoCBQCqiACWgLXMXJA3tWzJr06tlTCBcIgFJABUxAd0D4H9+9ndxYBmQ8eXD31ME9EEEgACpggrgUCNYtnPnl00cIe3pb7eePHyBsoAKQwyFg/9b1UBYDg4yCEtBxUA7Q4UDfAqlvXz5/ev8OIgQEzn4hL589gbCBCpiA4QFksXNwsrKxQUSBYPvqpY/u3oKwgQqYgCHGxcbMzMLi4BUIEQWCm5fPW7t4AhlAKaACUIgDQwwYHu8/fZnb23L64F4GRkYH74DozCI+bg4DKV5OVmYiooWBAQBSlKd9GixjLgAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-U-P {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAF6SURBVChTY/z//z8DA8Pff/8ff/jx8vPPzz9/XTp53NrOXpyXXVaAg5mJESjLBMTff/899fjj3bffvvz6++D2rWePHwIZQC5QECgFUgQ048Kzz99+gTi/f/06tH3Ty6dP/v/7B+QCBYFSQAWM999+A2oCCt27cW1KUyUHF9fr58+AZEFTt7KmDlBcWZiL8cSD90DD//37Wxjhl1HV9PH9u6tnT7qHRPZVFbXPXcHOycnDxsz0FWzr1bOnJGRkNQ2M2djY3r56KaOgrGdmefPyeaAUUAHI4UDw+/dvZhZWIOPzxw8iEpJABisb269fv8CSDEzcrMxASlPf6M61y/dvXuPh5we6+uP7t+ePHVZS1wJKARUgHH77ysWJ9WXSCkrPHt7/9+9fZEa+jZs3UBzk8D9//wHDAxIE3799Xb9w9stnjxMLqwSEhIEiXGzMZrL8TMAwNZDiBXKAQpxc3E4+QWKS0nAVQCmgAvRoAfrlyukT5lbWiGhhYAAAbkHMEz2QWQgAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-U-R {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAF3SURBVChTY/z//z8DA8Pff/8ff/jx5N2XXwxMQC43K7M4L7usAAczEyOQCxL6/vvvqccfm1tar9+4AdQCRF9+/b379htQ8NfXzyBFQDMuPPt85MD+VXOmXD9/BigEB8KfHjDsnsHw5xcT0JZvv/6umDkRKLp2wYw3L59DVMj+eCx/fvn/T2/+Xj/K9PLzT6DQg9s3gKSGvtGZw/vhKkBqgc69f4Hp6++/QJaJrSOQPH1or5ahicz3x1+3Tt126cHH77+Agv8/vWbce/sN0KV/fv++cemchIycIf+fRyt7Pn77tefqoyfvvzQEWOjIiTGeePAe6BeQuUi2PPvw9cHrT1P2XhTn55qQGcYEDA80FXMPXdWrWdK+9fTtlx+M5ESZFQ2YgCHGxcaM7NLXn78ByUuP32hKCmqqKDFrWoNC/Ne3Lwy7pgN9C1H068/fzRfuA4Pa0kBbLiSfkVcYGi3AEAOGB9C3QL8AeYx8IFuAZjCwsDEwMAAA6yrNGOnSx68AAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-W-B {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAF9SURBVChTY/z//z8DCPz7+/fjv7+f////DeQwMrIyMfMyM/MzMDABuSAMlPjy+e6d2xcWLlr569cvkMD/X3//vP396/Hvn99Bev7///vx4+0njx8nJJUB+T7eTnGxgdLS4kD2p/e/H9x6YmjtxAS0hZnpX0PjpDt3Ht64ce/o0bMQBwBVXD9/4/vXL88e3GUCuoORkVFaRkJRUVZAgM/cXP/duw8QFUClQPD6+WPGnz/uAB0B5EyavMjIUOvN2/dOdg6T+ue8fffeQFdLQ1WZkZEJoQhoC9BIoBmZmRXHTp399PkLNxdnUVaKlZkJE9C3YFOB3gapuHTqCtCDQT4eLCws+elJV27c4uLhYQKGB0QRxB2srCyS4mLnLl7R09I4cfa8soK8qKQsEzDEgIYhuzQ6NICZmenrt29AFd4erlIKyqAQ//3r+8UTR4C+hSgCgms3b3Nzc/1jYAqNjufk4oZGy9+/f4HhAfTtty8gpUB3AG0BmsHMzMzAwAAAzY/G/vJiHAIAAAAASUVORK5CYII=') no-repeat;
	    }
	    
	    .mana-W {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAGLSURBVChTY/gPBX///Hn36+fDT5+ubVg/B8gAcoGCEDkmBgagut+3bx3/++ftj59fAgMz3n/4+P//LyD396/HQCmgAqCif39+P5swcc6lyze/ff3x6/fvvv75r1+/Ky5p6+icevPGCaACRqCxQE129pFXr922sTHh5uL8/Pmrnp7GjJnLtm6ZY2FuwMwizPTv72eggRvWz4iI8Pn08fPOXYePHT8HRMrKcjw8XF+/fgMqYNy5YwkjI2Nbx3QuLs5Dh04BNUCAk6Plrdv3RUWFtm6Zy2RsrFta3vHo0TM2VhaoPBh8+fKVn483Oytm756jjEDfvn37+vOXrwWFLR/efwQ6H2iwvr6mpYVBWWkaHx8PIyMbExMzr5AQ/7ev34F2mZnrA6WBFrGwME+fsSw5pRJoJFABEzMz/717z+cvWOPhbldZnvH27fvXr98unN+1f99SKSkxRkZWoAJQiP/79+vXzwc/f9wGookTG0PD/L5+uQFk37p1FCgFVIAeLevXzf7+7RZKtPz/DwBg2QLLp+LstgAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-W-P {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFpSURBVChTY/gPBX///Hn36+fDb19v7di+BMgAcoGCEDkmBgagut+/fz3+++ft//+/rl+/c//BYyADyAUKAqWACoCK/v35/QzC+fXr95q1Ox4+fPbv3z+IZqAUUAHT378fISouXb7p5pF0+szlDRv32NhGXrh4HaIOqIABaP3PH7e/fb1pampy6OCadWtnFxdnXr6829LK4v27S0ApoAImiDHHjp1TUJA2N9dn52B79vyVmqqCna3JmTNXIIaBHA4Ev37/ZmFlATI+vP8kLSUOZLCzs/34+QssycDEyMgKpMxM9S6cv3758i1+AV6gn9+8eb9333E9XXWgFFABIzA8gL4Fcs6du5qV06iqIn/n7qO/f/9WVqQHBrgCxZlZhBmBIQYPjy9fvk2esvjhw6fNTQWiokIQY1jZZIFuYmJhlYJYysPDFRnhIyMjCVcBlAIqADkcohxkLCObgoKMg70ZkAHkAgVBmhkYAPMk1o1WW4JjAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-W-U {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFwSURBVChTRVFNSwJRFH3vTZN9ma5SsiFsEwQRtshNi1YRtDJaVkar/kBBu+on2C9I2lQrN61ctEgoSMqEtBq1UosBv1KrmdGZ6UwTduE97rnvcO6951HDMIgZuqZ96FrDMFoAlPKMs3OcgxAGaB48NBsZ8en2MHysqqpZMFStXW6pebXdBqELGvV6tpDPr29sAxeL0tpqwONxIa/Ktky1OSM4GLpwTN/dC4niSzqdjcXi1gA1ZSAp8V+qlq/JDHNQSj0jbq9XcDoH/f6pSqVmMUBFSA2FKrKIIQBCB+Fp30SpXJ1bCJzflVOJ+Oz8IuqUkn8SukASGjcFshVcGp/0be7sWySGbZH9ApOBLtHIae7hPho5eX5Mod7Pcwx+WKTOHImrC9yuYSF5fWkmdhuDYxDrMBBuYRT322uuJL33dXOCs8d0HMbFC01sa5EU+fvs5AjJ8krQPzbUy3N/36LpBvzAtp8tk4o50AUaHKOEkB8/eLy7BZycwQAAAABJRU5ErkJggg==') no-repeat;
	    }
	    
	    .mana-X {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url('data:image/png; base64,iVBORw0KGgoAAAANSUhEUgAAAAwAAAAMCAIAAADZF8uwAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAAFdSURBVChTY/z//z8DA8O/f3/fvHz+/u2rnz++A7nsHJyCwmIi4pJMTMxALkjRt69fTh49+PPnDyCfl4eHi5vr5ctXQDYXF7e5jQM7OwfD379/zp48nBgfy8PLr6SkvGzhnNPH9nt7eYqIiFWVl1y/dAaogAVoCzMjQ352moS42Oz5Szg5OVlZWORkpYP8vY0N9YG2gxSkJMT8+fMbaLiOlsbzFy8XLVvFwswsLiZqY2UBFASCP79/MUFcCgFF+ZlCggIr1mxwtLeBCjEwABUwQZlg8O7deyVF+d+/f0+cNhsqBAZMQN9CWF++fp27YGledlp7U83W7bs3bd0JEQcqYAKGB0jFl69Vda0OdlYc7OzqaiqRYUF9k6YfOXYSKAVUwAQMMaDaWfMWAx177MRpoF0vXr56//69q5P9wcPHbt65B1QACkxgMN6/dRXZBxAA1Kyopg0MTCKihYEBAH+uo0BN0hOvAAAAAElFTkSuQmCC') no-repeat;
	    }
	    
	    .mana-C {
	        display: inline-block;
	        width: 12px;
	        height: 12px;
	        \#padding-left: 12px;
	        background: url(data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAAQABAAD/2wBDAAEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/2wBDAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQEBAQH/wAARCAAMAAwDAREAAhEBAxEB/8QAFQABAQAAAAAAAAAAAAAAAAAACQP/xAAfEAACAwEBAQEAAwAAAAAAAAACAwQFBgEHCBQSFyH/xAAYAQACAwAAAAAAAAAAAAAAAAAABAIDBf/EACURAAIBAwMEAgMAAAAAAAAAAAECEQMSIQAxUQQTQWEjoTJSgf/aAAwDAQACEQMRAD8ATr7G+yvddx7tsMfjNZnvGP6Pz5e031t7Q4qWh9WzdUzvAwWAEyMI+IUBnE3XoEbrbGiuGU8ZNTI7IawkCbyWa5rjaoXNk8j9hiB963FUUgKdMKgQXMzR8nqdyreT/ANJ78ofcGz9B8LxeyfhtdTBfw/3xabfwGw9JVRTBXAiN/kRMl15GLJNRYM4sptbIiv4lIkKxkKr05Qy8HDLBkb75zqt+lpVj3I7dwyu2eYjz96l9x/JXhHom4wE7ZYqLelQa6HvqNEwgKNV6GOwun2OAqE2Vc1nQdY0stkmrmuRGN0Uvzp4BWUIxtkXmCPGRuPed9HSua1IdyGNP8SRnG08++caSDy/y/F57F1EWLUJl9lpCykybIFSpTpUpSuH3p8UoAWAKWtSlrAAAOf50ukRM06aooAHsk5JJ0hXr1XqsSxEEqApKiFJjE78nX//2Q==) no-repeat;
	    }
    </style>
</head>
<body>
	<ul id="top">
			<li style="background-color:yellow;"><a href="#white" style="color:black">White Cards</a></li>
			<li style="background-color:blue;"><a href="#blue">Blue Cards</a></li>
			<li style="background-color:black;"><a href="#black">Black Cards</a></li>
			<li style="background-color:red;"><a href="#red">Red Cards</a></li>
			<li style="background-color:green;"><a href="#green">Green Cards</a></li>
			<li style="background-color:gold;"><a href="#multi" style="color:black">Multi-colored Cards</a></li>
			<li style="background-color:lightgrey;"><a href="#colorless" style="color:black">Colorless Cards</a></li>
			<li style="background-color:darkgoldenrod;"><a href="#lands" style="color:black">Lands Cards</a></li>
	</ul>
	<hr>
"""
