#include <stdio.h>
///look for ways to eliminate dynamic memory allocation ie for example do the same linked list stuff but with statically allocated stuff
//-> pass an already existing menu item to the add function, and let the add function fill the next and prev slots
#ifndef LCDMENU_H
#define LCDMENU_H
class MenuItem
{
  
  private:
    boolean isInSetMode;

 public:
  MenuItem(char* txt);
  MenuItem *next;
  MenuItem *prev;
  MenuItem *child;
  MenuItem *parent;
   
  void add_sibling(boolean after, MenuItem *sibling);
  MenuItem* last_sibling();
  MenuItem* first_sibling();
  MenuItem* next_sibling();
  MenuItem* prev_sibling();
  //////////
  void add_child(MenuItem * child);
  
  MenuItem* get_child(int index);
  MenuItem* get_parent();
  MenuItem* top();
  MenuItem* bottom();
  
  
  //int nbChildren;
  char* text;
  virtual void set();
  virtual void print();
  virtual void nextValue();
  virtual void prevValue();
};

class BoolMenu:public MenuItem
{
  private:
    boolean value;
  public:
    BoolMenu(char* txt,boolean val);
    void print();
    void nextValue();
    void prevValue();
  
};

class NumericMenu:public MenuItem
{
  private:
    int value;
    int increment;
    Heater* heater;
    void(Heater::*setter)(int);
    
   public:
     NumericMenu(char* txt, int val, int inc, Heater * htr, void(Heater::*setr)(int));
     void print();
     void nextValue();
     void prevValue();
     void set();
};


class InfoMenu:public MenuItem
{
  private:
      Heater *heater;
     int(Heater::*getter)(void);
   public:
     InfoMenu(char* txt, Heater * htr, int(Heater::*gettr)(void));
     
     void print();

};



class LcdMenu
{
    private:     
      //uint8_t index;
     // int nbItems;
      
    public:
      MenuItem *currentItem;
      LcdMenu();
      //LcdMenu(char* upperItems[]);
      //void add_item(char* text);
      void add_item(MenuItem *menuItem);
      void next();
      void prev();
      void down();
      void up();
      MenuItem * last();
      MenuItem * first();
      void printStuff();
      char* currentText();
      
      
};


#endif
