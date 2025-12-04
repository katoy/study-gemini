package com.example;

import processing.core.PApplet;
import processing.core.PFont;

public class DropDown {
  PApplet p;
  float x, y, w, h;
  String label;
  public String[] options;
  public boolean expanded = false;
  String selected;
  PFont japaneseFont;
  
  public DropDown(PApplet p, float x, float y, float w, float h, String label, String[] options, PFont font) {
    this.p = p;
    this.x = x; this.y = y; this.w = w; this.h = h;
    this.label = label;
    this.options = options;
    if (options.length > 0) {
      this.selected = options[0];
    } else {
      this.selected = "";
    }
    this.japaneseFont = font;
  }
  
  public String getSelected() { return selected; }
  
  public void handleMousePress() {
    if (p.mouseX > x && p.mouseX < x + w && p.mouseY > y && p.mouseY < y + h) {
      expanded = !expanded;
    } else if (expanded) {
      for (int i = 0; i < options.length; i++) {
        if (p.mouseX > x && p.mouseX < x + w && p.mouseY > y + h * (i + 1) && p.mouseY < y + h * (i + 2)) {
          selected = options[i];
          expanded = false;
          return;
        }
      }
      expanded = false;
    }
  }
  
  public void draw() {
    // Label
    p.textFont(japaneseFont);
    p.fill(0);
    p.textAlign(PApplet.LEFT, PApplet.CENTER);
    p.textSize(16);
    p.text(label, x, y - 20);

    // Dropdown box
    p.fill(255);
    p.stroke(0);
    p.rect(x, y, w, h);
    p.fill(0);
    p.textAlign(PApplet.LEFT, PApplet.CENTER);
    p.text(selected, x + 10, y + h/2);

    // Arrow
    p.fill(0);
    p.triangle(x + w - 20, y + h/2 - 5, x + w - 10, y + h/2 - 5, x + w - 15, y + h/2 + 5);
  }

  public void drawExpandedOptions() {
    if (expanded) {
      for (int i = 0; i < options.length; i++) {
        p.fill(255);
        p.stroke(0);
        p.rect(x, y + h * (i + 1), w, h);
        p.fill(0);
        p.textFont(japaneseFont);
        p.text(options[i], x + 10, y + h * (i + 1) + h/2);
      }
    }
  }
}
