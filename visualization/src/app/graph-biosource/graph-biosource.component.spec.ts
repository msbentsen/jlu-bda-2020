import { ComponentFixture, TestBed } from '@angular/core/testing';

import { GraphBiosourceComponent } from './graph-biosource.component';

describe('GraphBiosourceComponent', () => {
  let component: GraphBiosourceComponent;
  let fixture: ComponentFixture<GraphBiosourceComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ GraphBiosourceComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(GraphBiosourceComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
