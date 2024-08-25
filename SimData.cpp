// Downloaded from https://developer.x-plane.com/code-sample/simdata/


/*
 * SimData.c
 * 
 * This example demonstrates how to interact with X-Plane by reading and writing
 * data.  This example creates menus items that change the nav-1 radio frequency.
 * 
 */

#include <stdio.h>
#include <string.h>
#include "XPLMDataAccess.h"
#include "XPLMMenus.h"

/* We keep our data ref globally since only one is used for the whole plugin. */
static XPLMDataRef		gDataRef = NULL;

static void	MyMenuHandlerCallback(
                                   void *               inMenuRef,    
                                   void *               inItemRef);    

PLUGIN_API int XPluginStart(
						char *		outName,
						char *		outSig,
						char *		outDesc)
{
		XPLMMenuID	myMenu;
		int			mySubMenuItem;

	/* Provide our plugin's profile to the plugin system. */
	strcpy(outName, "SimData");
	strcpy(outSig, "xplanesdk.examples.simdata");
	strcpy(outDesc, "A plugin that changes sim data.");

	/* First we put a new menu item into the plugin menu.
	 * This menu item will contain a submenu for us. */
	mySubMenuItem = XPLMAppendMenuItem(
						XPLMFindPluginsMenu(),	/* Put in plugins menu */
						"Sim Data",				/* Item Title */
						0,						/* Item Ref */
						1);						/* Force English */
	
	/* Now create a submenu attached to our menu item. */
	myMenu = XPLMCreateMenu(
						"Sim Data", 
						XPLMFindPluginsMenu(), 
						mySubMenuItem, 			/* Menu Item to attach to. */
						MyMenuHandlerCallback,	/* The handler */
						0);						/* Handler Ref */
						
	/* Append a few menu items to our submenu.  We will use the refcon to
	 * store the amount we want to change the radio by. */
	XPLMAppendMenuItem(
						myMenu,
						"Decrement Nav1",
						(void *) -1000,
						1);
	XPLMAppendMenuItem(
						myMenu,
						"Increment Nav1",
						(void *) +1000,
						1);
	
	/* Look up our data ref.  You find the string name of the data ref
	 * in the master list of data refs, including in HTML form in the 
	 * plugin SDK.  In this case, we want the nav1 frequency. */
	gDataRef = XPLMFindDataRef("sim/cockpit/radios/nav1_freq_hz");
	
	/* Only return that we initialized correctly if we found the data ref. */
	return (gDataRef != NULL) ? 1 : 0;
}

PLUGIN_API void	XPluginStop(void)
{
}

PLUGIN_API void XPluginDisable(void)
{
}

PLUGIN_API int XPluginEnable(void)
{
	return 1;
}

PLUGIN_API void XPluginReceiveMessage(
					XPLMPluginID	inFromWho,
					int				inMessage,
					void *			inParam)
{
}

void	MyMenuHandlerCallback(
                                   void *               inMenuRef,    
                                   void *               inItemRef)
{
	/* This is our handler for the menu item.  Our inItemRef is the refcon
	 * we registered in our XPLMAppendMenuItem calls.  It is either +1000 or
	 * -1000 depending on which menu item is picked. */
	if (gDataRef != NULL)
	{
		/* We read the data ref, add the increment and set it again.
		 * This changes the nav frequency. */
		XPLMSetDatai(gDataRef, XPLMGetDatai(gDataRef) + (int) inItemRef);
	}
}                                   



