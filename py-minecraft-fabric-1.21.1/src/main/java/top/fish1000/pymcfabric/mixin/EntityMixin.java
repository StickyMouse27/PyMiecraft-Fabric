package top.fish1000.pymcfabric.mixin;

import org.spongepowered.asm.mixin.Mixin;
import org.spongepowered.asm.mixin.injection.Inject;
import org.spongepowered.asm.mixin.injection.callback.CallbackInfoReturnable;
import org.spongepowered.asm.mixin.injection.At;

import net.minecraft.entity.Entity;
import net.minecraft.util.ActionResult;
import top.fish1000.pymcfabric.PymcMngr;

@Mixin(Entity.class)
public abstract class EntityMixin {
    @Inject(method = "interact(Lnet/minecraft/entity/player/PlayerEntity;Lnet/minecraft/util/Hand;)Lnet/minecraft/util/ActionResult;", at = @At("HEAD"))
    private void entityInteract(CallbackInfoReturnable<ActionResult> info) {
        PymcMngr.tick("entity interact", ((Entity) (Object) this));
        System.out.println("entity interact: " + ((Entity) (Object) this).getName().getString());
    }
}
