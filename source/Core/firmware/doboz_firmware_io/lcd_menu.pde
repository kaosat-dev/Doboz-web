#include "lcd_menu.h"

MenuItem::MenuItem(char* txt)
{
  text=txt;
  prev=NULL;
  next=NULL;
  parent=NULL;
  child=NULL;

}

void MenuItem::add_sibling(boolean after, MenuItem* sibling)
{

    if(after)
    {
      MenuItem *tmp=last_sibling();
      Serial.println(tmp->text);
      tmp->next=sibling;
      sibling->prev=tmp;
      sibling->next=NULL;
    }
    else
    {
      prev=sibling;
      sibling->next=this;
    }
    
}


MenuItem* MenuItem::next_sibling()
{
  if(next!=NULL)
  {
   return next;
  }
  else
  { return first_sibling();}
}

MenuItem* MenuItem::prev_sibling()
{
   if(prev!=NULL)
  {
   return prev;
  }
    else
  { return last_sibling();}
 
}

MenuItem* MenuItem::last_sibling()
{
  MenuItem* tmp=this;
  while(tmp->next!=NULL )
  {
    tmp=tmp->next;
  }
   return tmp;
}

MenuItem* MenuItem::first_sibling()
{
  MenuItem* tmp=this;
  while(tmp->prev!=NULL)
  {
    tmp=tmp->prev;
  }
   return tmp;
}

////////
void MenuItem::add_child(MenuItem* chld)
{
  chld->parent=this;
  if(child==NULL)
  {
    child=chld;
  }
  else
  {
    child->add_sibling(true,chld);
  }
}

MenuItem* MenuItem::get_child(int indx)
{
  if(child!=NULL)
  {
      MenuItem* tmp=child;
      int index=0;
      while(index<indx && tmp->next!=NULL)
      {
        tmp=tmp->next;
      }
      return tmp;
  
   
  }
  return NULL;
}

MenuItem* MenuItem::get_parent()
{
  if(parent!=NULL)
  {
   return parent;
  }
  return NULL;
}

MenuItem* MenuItem::top()
{
  MenuItem* tmp=this;
  while(tmp->parent!=NULL)
  {
    tmp=tmp->parent;
  }
   return tmp;
}
MenuItem* MenuItem::bottom()
{
 MenuItem* tmp=this;
  while(tmp->child!=NULL)
  {
    tmp=tmp->child;
  }
   return tmp;
}



void MenuItem::print()
{  
    clear_lcd();
    setCursor(1,0); 
    if(prev!=NULL)
    {
      print_lcd('^');
    }
    
    
    print_lcd_str(text);
    if(child!=NULL)
    {
      setCursor(1,15); 
      print_lcd('>');
    }
}
void MenuItem::set()
{
  isInSetMode!=isInSetMode;
}

void MenuItem::nextValue()
{
}
void MenuItem::prevValue()
{
}


BoolMenu::BoolMenu(char* txt,boolean val):MenuItem(txt)
{
    value=val;
}

void BoolMenu::print()
{
  clear_lcd();
  setCursor(1,0); 
  print_lcd_str(text);
  if(value)
  {
    print_lcd_str(" YES");
  }
  else
  {
    print_lcd_str(" NO");
  }
}


void BoolMenu::nextValue()
{
  value=!value;
  print();
}
void BoolMenu::prevValue()
{
  value=!value;
  print();
}


NumericMenu::NumericMenu(char* txt,int val, int inc, Heater * htr, void(Heater::*setr)(int)): MenuItem(txt)
{
  value=val;
  increment=inc;
  heater=htr;
  setter=setr;
}

void NumericMenu::print()
{
  clear_lcd();
  setCursor(1,0); 
  if(prev!=NULL)
    {
      print_lcd('^');
    }
  
  
  print_lcd_str(text);
  print_lcd_str(" ");
  char buf[4];
  itoa(value,buf,10);
  print_lcd_str(buf);
  
  if(child!=NULL)
    {
      setCursor(1,16); 
      print_lcd('>');
    }
}

void NumericMenu::nextValue()
{
  value+=increment;
  print();
}
void NumericMenu::prevValue()
{
  value-=increment;
  print();
}

void NumericMenu::set()
{
    (heater->*setter)(value);
}



InfoMenu::InfoMenu(char* txt, Heater *htr, int(Heater::*gettr)(void)): MenuItem(txt)
{
    heater=htr;
    getter=gettr;
}

void InfoMenu::print()
{
  clear_lcd();
  setCursor(1,0); 
  print_lcd_str(text);
  print_lcd_str(" ");
  char buf[4];
  int tmp=(heater->*getter)();
  itoa(tmp,buf,10);
  print_lcd_str(buf);
  
  
}

/*InfoMenu::InfoMenu(char* txt,int val, int inc): MenuItem(txt)
{
  value=val;
  increment=inc;
}

void NumericMenu::print()
{
  clear_lcd();
  setCursor(1,0); 
  if(prev!=NULL)
    {
      print_lcd('^');
    }
  
  
  print_lcd_str(text);
  print_lcd_str(" ");
  char buf[4];
  itoa(value,buf,10);
  print_lcd_str(buf);
  
  if(child!=NULL)
    {
      setCursor(1,16); 
      print_lcd('>');
    }
}
*/











/////////////////////////////////////////////

LcdMenu::LcdMenu()
{
   
    /*MenuItem *tmp= new MenuItem();
    tmp->next=NULL;
    tmp->prev=NULL;
    tmp->text="Home";
    currentItem=tmp;*/
    //MenuItem Kpouer =(MenuItem){0,0,0,"Home"};
    currentItem=0;
}




void LcdMenu::add_item(MenuItem *menuItem)
{
      if(currentItem!=0)
      {
          MenuItem* tmp=last();
          menuItem->next=0;
          menuItem->prev=tmp;
          tmp->next=menuItem;

          }
      else
       {
         currentItem=menuItem;
          
       }
      
}



MenuItem* LcdMenu::last()
{
  MenuItem  *tmp=currentItem;
  while(tmp->next!=0)
  {
    tmp=tmp->next;
   
  } 
  return tmp;
  
}
MenuItem * LcdMenu::first()
{
  MenuItem  *tmp=currentItem;
  while(currentItem->prev!=0)
  {
    tmp=tmp->prev;
  } 
   return tmp;
}

void LcdMenu::next()
{
 
  if(currentItem->next!=0)
  {
     currentItem=currentItem->next;  
     this->printStuff();
  }
}


void LcdMenu::prev()
{
  
  if(currentItem->prev!=0)
  {
     currentItem=currentItem->prev; 
      this->printStuff();
  }
}




void LcdMenu::printStuff()
{ 
    clear_lcd();
    setCursor(1,0); 
   currentItem->print();
    
    if(currentItem->next!=0)
    {
      setCursor(2,0);
      currentItem->next->print();
    }
}
