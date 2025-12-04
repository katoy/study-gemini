package com.example;

import processing.core.PApplet;
import processing.core.PFont;

public class RadioButton {
  PApplet p;
  String label;
  float x, y;
  public boolean isSelected;
  PFont japaneseFont;
  
  public RadioButton(PApplet p, String label, float x, float y, boolean isSelected, PFont font) {
    this.p = p;
    this.label = label;
    this.x = x;
    this.y = y;
    this.isSelected = isSelected;
    this.japaneseFont = font;
  }
  
  public void draw() {
    p.stroke(0);
    p.fill(isSelected ? 0 : 255);
    p.ellipse(x, y, 20, 20);
    p.fill(0);
    p.textAlign(PApplet.LEFT, PApplet.CENTER);
    p.textFont(japaneseFont, 16);
    p.text(label, x + 15, y);
  }
  
  public boolean isClicked() {
    return p.mousePressed && p.dist(p.mouseX, p.mouseY, x, y) < 10;
  }
}
