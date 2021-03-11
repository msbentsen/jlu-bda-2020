import { ComponentFixture, TestBed } from '@angular/core/testing';

import { SingleTfComponent } from './single-tf.component';

describe('SingleTfComponent', () => {
  let component: SingleTfComponent;
  let fixture: ComponentFixture<SingleTfComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ SingleTfComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(SingleTfComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
