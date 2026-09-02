model FirstOrder
  "Tiny smoke-test model for DymolaAgenticAI"
  parameter Real k = 1.0 "Gain";
  parameter Real T = 0.5 "Time constant";
  Real u = 1.0 "Step input";
  Real y(start=0) "Output";
equation
  T * der(y) = k * u - y;
  annotation(experiment(StopTime=5));
end FirstOrder;
