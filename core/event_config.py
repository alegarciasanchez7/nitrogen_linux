"""
Estructura de datos para un evento de simulación
"""
class EventConfig:
    def __init__(self, name="Nuevo Evento", frequency=1000):
        self.name = name
        self.frequency = frequency
        self.variables = [] # Lista de objetos Variable
        self.enabled = True

    def __str__(self):
        return f"{self.name} ({self.frequency}ms)"
    
    def to_dict(self):
        """Convierte el evento a un diccionario serializable"""
        return {
            "name": self.name,
            "frequency": self.frequency,
            "enabled": self.enabled,
            "variables": [self._variable_to_dict(var) for var in self.variables]
        }
    
    @staticmethod
    def from_dict(data):
        """Crea un EventConfig desde un diccionario"""
        from variables_type import NumericVariable, StringVariable, ListVariable, DateVariable, PointVariable, BooleanVariable
        
        event = EventConfig(
            name=data.get("name", "Evento"),
            frequency=data.get("frequency", 1000)
        )
        event.enabled = data.get("enabled", True)
        
        # Reconstruir variables
        for var_data in data.get("variables", []):
            var = EventConfig._variable_from_dict(var_data)
            if var:
                event.variables.append(var)
        
        return event
    
    @staticmethod
    def _variable_to_dict(var):
        """Convierte una variable a diccionario"""
        var_dict = {
            "type": var.__class__.__name__,
            "name": var.name,
            "anomaly_prob": getattr(var, "anomaly_prob", 0),
            "anomaly_value": getattr(var, "anomaly_value", "ERR")
        }
        
        # Añadir propiedades específicas según el tipo
        if var.__class__.__name__ == "NumericVariable":
            var_dict.update({
                "min_val": var.min_val,
                "max_val": var.max_val,
                "strategy": var.strategy,
                "step": var.step
            })
        elif var.__class__.__name__ == "StringVariable":
            var_dict.update({
                "strategy": var.strategy,
                "pattern": getattr(var, "pattern", ""),
                "min_len": getattr(var, "min_len", 5),
                "max_len": getattr(var, "max_len", 10),
                "use_upper": getattr(var, "use_upper", True),
                "use_nums": getattr(var, "use_nums", True),
                "use_sym": getattr(var, "use_sym", False)
            })
        elif var.__class__.__name__ == "ListVariable":
            var_dict.update({
                "values": var.values,
                "strategy": var.strategy
            })
        elif var.__class__.__name__ == "DateVariable":
            var_dict.update({
                "strategy": var.strategy,
                "date_format": var.date_format
            })
        elif var.__class__.__name__ == "PointVariable":
            var_dict.update({
                "dimension": var.dimension,
                "x_range": var.x_range,
                "y_range": var.y_range,
                "z_range": var.z_range,
                "strategy": var.strategy,
                "step": var.step
            })
        elif var.__class__.__name__ == "BooleanVariable":
            var_dict.update({
                "strategy": var.strategy,
                "true_prob": var.true_prob,
                "initial_value": var.current_value
            })
        
        return var_dict
    
    @staticmethod
    def _variable_from_dict(var_data):
        """Reconstruye una variable desde un diccionario"""
        from variables_type import NumericVariable, StringVariable, ListVariable, DateVariable, PointVariable, BooleanVariable
        
        # Soportar tanto "type" como "__type__" para compatibilidad
        var_type = var_data.get("type") or var_data.get("__type__")
        name = var_data.get("name")
        anomaly_prob = var_data.get("anomaly_prob", 0)
        anomaly_value = var_data.get("anomaly_value", "ERR")
        
        if var_type == "NumericVariable":
            return NumericVariable(
                name, 
                var_data["min_val"], 
                var_data["max_val"],
                strategy=var_data.get("strategy", "random"),
                step=var_data.get("step", 1),
                anomaly_prob=anomaly_prob,
                anomaly_value=anomaly_value
            )
        elif var_type == "StringVariable":
            if var_data.get("strategy") == "regex":
                return StringVariable(
                    name,
                    strategy="regex",
                    pattern=var_data.get("pattern", ""),
                    anomaly_prob=anomaly_prob,
                    anomaly_value=anomaly_value
                )
            else:
                return StringVariable(
                    name,
                    strategy="random",
                    min_len=var_data.get("min_len", 5),
                    max_len=var_data.get("max_len", 10),
                    use_upper=var_data.get("use_upper", True),
                    use_nums=var_data.get("use_nums", True),
                    use_sym=var_data.get("use_sym", False),
                    anomaly_prob=anomaly_prob,
                    anomaly_value=anomaly_value
                )
        elif var_type == "ListVariable":
            return ListVariable(
                name,
                var_data.get("values", []),
                strategy=var_data.get("strategy", "random"),
                anomaly_prob=anomaly_prob,
                anomaly_value=anomaly_value
            )
        elif var_type == "DateVariable":
            return DateVariable(
                name,
                strategy=var_data.get("strategy", "now"),
                date_format=var_data.get("date_format", "%H:%M:%S"),
                anomaly_prob=anomaly_prob,
                anomaly_value=anomaly_value
            )
        elif var_type == "PointVariable":
            return PointVariable(
                name,
                dimension=var_data.get("dimension", 3),
                x_range=tuple(var_data.get("x_range", [0, 100])),
                y_range=tuple(var_data.get("y_range", [0, 100])),
                z_range=tuple(var_data.get("z_range", [0, 100])),
                strategy=var_data.get("strategy", "random"),
                step=var_data.get("step", 1.0),
                anomaly_prob=anomaly_prob,
                anomaly_value=anomaly_value
            )
        elif var_type == "BooleanVariable":
            return BooleanVariable(
                name,
                strategy=var_data.get("strategy", "random"),
                true_prob=var_data.get("true_prob", 50.0),
                initial_value=var_data.get("initial_value", True),
                anomaly_prob=anomaly_prob,
                anomaly_value=anomaly_value
            )
        
        return None